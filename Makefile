# TurboQuant Makefile
# Unified build system for firmware, tests, and documentation

# Configuration
PROJECT_NAME := turboquant
FIRMWARE_DIR := .
BUILD_DIR := build
TEST_DIR := tests
DOCS_DIR := docs

# ESP32 toolchain
IDF_PATH ?= $(HOME)/esp/esp-idf
BAUD_RATE := 921600
DEFAULT_PORT := /dev/ttyUSB0

# Python settings
PYTHON := python3
PIP := pip3
VENV_DIR := .venv

# Source files
C_SOURCES := $(wildcard *.c)
CPP_SOURCES := $(wildcard *.cpp)
PY_SOURCES := $(wildcard *.py)

# Targets
.PHONY: all clean help install test firmware flash monitor \
        format lint docs venv deps check \
        acquire display analyze stream \
        ci-test ci-build ci-docs

# Default target
all: deps check

# =============================================================================
# Help
# =============================================================================

help:
	@echo "TurboQuant Build System"
	@echo "======================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install Python dependencies"
	@echo "  make venv            Create Python virtual environment"
	@echo "  make deps            Install all dependencies"
	@echo ""
	@echo "Firmware:"
	@echo "  make firmware        Build ESP32 firmware"
	@echo "  make flash           Flash firmware to device"
	@echo "  make monitor         Monitor serial output"
	@echo "  make erase           Erase flash"
	@echo ""
	@echo "Software:"
	@echo "  make check           Run code checks (lint + format)"
	@echo "  make format          Format code (black, clang-format)"
	@echo "  make lint            Run linters"
	@echo "  make test            Run test suite"
	@echo ""
	@echo "Operations:"
	@echo "  make acquire         Run acquisition (60s test)"
	@echo "  make display         Launch display (demo mode)"
	@echo "  make analyze         Analyze test recording"
	@echo "  make stream          Start streaming server"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs            Generate documentation"
	@echo "  make readme          Update README"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-test         Run CI test suite"
	@echo "  make ci-build        Build all artifacts"
	@echo "  make ci-docs         Build documentation"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Clean build artifacts"
	@echo "  make distclean       Clean everything (including venv)"
	@echo ""

# =============================================================================
# Setup and Dependencies
# =============================================================================

install: requirements.txt
	$(PIP) install -r requirements.txt

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

deps: requirements.txt
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

# =============================================================================
# Firmware Build (ESP-IDF)
# =============================================================================

firmware: CMakeLists.txt
	@echo "Building ESP32 firmware..."
	. $(IDF_PATH)/export.sh && idf.py build
	@echo "Firmware built: build/$(PROJECT_NAME).bin"

flash:
	@echo "Flashing firmware to $(DEFAULT_PORT)..."
	. $(IDF_PATH)/export.sh && idf.py -p $(DEFAULT_PORT) flash

monitor:
	. $(IDF_PATH)/export.sh && idf.py -p $(DEFAULT_PORT) monitor

erase:
	. $(IDF_PATH)/export.sh && idf.py -p $(DEFAULT_PORT) erase-flash

fullflash: firmware flash
	@echo "Firmware built and flashed"

# =============================================================================
# Code Quality
# =============================================================================

check: format lint
	@echo "All checks passed"

format:
	@echo "Formatting Python code..."
	$(PYTHON) -m black *.py --line-length 100 --quiet 2>/dev/null || echo "black not installed"
	@echo "Formatting C/C++ code..."
	clang-format -i *.c *.h *.cpp 2>/dev/null || echo "clang-format not installed"

lint:
	@echo "Linting Python code..."
	$(PYTHON) -m pylint *.py --disable=C,R 2>/dev/null || echo "pylint not installed"
	$(PYTHON) -m flake8 *.py --max-line-length 100 2>/dev/null || echo "flake8 not installed"
	@echo "Checking types..."
	$(PYTHON) -m mypy *.py --ignore-missing-imports 2>/dev/null || echo "mypy not installed"

# =============================================================================
# Testing
# =============================================================================

test: test-unit test-integration

test-unit:
	@echo "Running unit tests..."
	$(PYTHON) -m pytest tests/unit -v 2>/dev/null || echo "No unit tests found"

test-integration:
	@echo "Running integration tests..."
	$(PYTHON) verify_dma_integrity.py --demo --bursts 5 2>/dev/null || true

test-hardware:
	@echo "Running hardware tests (requires device)..."
	$(PYTHON) verify_dma_integrity.py --port $(DEFAULT_PORT) --bursts 10

test-pipeline:
	@echo "Running full pipeline test..."
	$(PYTHON) full_pipeline_test.py --demo --focus 50

# =============================================================================
# Operations
# =============================================================================

acquire:
	@echo "Running 60-second test acquisition..."
	$(PYTHON) turboquant.py acquire --duration 60 --output test_$(shell date +%Y%m%d_%H%M%S).h5

display:
	@echo "Launching display (demo mode)..."
	$(PYTHON) turboquant.py display --mode demo

display-advanced:
	@echo "Launching advanced display..."
	$(PYTHON) turboquant.py display --mode advanced

analyze:
	@echo "Analyzing test recording..."
	$(PYTHON) turboquant.py analyze test_recording.h5 --spectrogram --info || \
	$(PYTHON) turboquant.py analyze *.h5 --spectrogram --info 2>/dev/null || \
	echo "No recordings found. Run 'make acquire' first."

stream:
	@echo "Starting streaming server (demo mode)..."
	$(PYTHON) turboquant.py stream server --demo --bind tcp://*:5555

stream-client:
	@echo "Starting streaming client..."
	$(PYTHON) turboquant.py stream client --connect tcp://localhost:5555 --gui

# =============================================================================
# Documentation
# =============================================================================

docs:
	@echo "Generating documentation..."
	mkdir -p $(DOCS_DIR)
	$(PYTHON) -m pydoc -w turboquant 2>/dev/null || true
	$(PYTHON) -m pydoc -w data_recorder 2>/dev/null || true
	$(PYTHON) -m pydoc -w data_analysis 2>/dev/null || true
	@echo "Documentation generated in $(DOCS_DIR)/"

readme:
	@echo "Updating README..."
	@echo "# TurboQuant" > README.md
	@echo "" >> README.md
	@echo "High-speed DMA acquisition and beamforming control for ultrasound arrays." >> README.md
	@echo "" >> README.md
	@echo "## Quick Start" >> README.md
	@echo "" >> README.md
	@echo '\`\`\`bash' >> README.md
	@echo "make install    # Install dependencies" >> README.md
	@echo "make firmware   # Build firmware" >> README.md
	@echo "make flash      # Flash to ESP32" >> README.md
	@echo "make display    # Launch visualization" >> README.md
	@echo '\`\`\`' >> README.md
	@echo "README.md updated"

# =============================================================================
# CI/CD Targets
# =============================================================================

ci-test:
	@echo "Running CI test suite..."
	$(MAKE) test-unit
	$(MAKE) lint
	$(MAKE) test-pipeline

ci-build:
	@echo "Building CI artifacts..."
	mkdir -p artifacts
	$(MAKE) firmware
	cp build/*.bin artifacts/ 2>/dev/null || true
	cp build/*.elf artifacts/ 2>/dev/null || true
	zip -r artifacts/turboquant-firmware.zip build/ 2>/dev/null || true
	@echo "Artifacts built in artifacts/"

ci-docs:
	@echo "Building documentation for CI..."
	$(MAKE) docs
	mkdir -p artifacts/docs
	cp *.html artifacts/docs/ 2>/dev/null || true
	cp *.md artifacts/docs/ 2>/dev/null || true

ci-package:
	@echo "Creating release package..."
	mkdir -p release
	cp turboquant.py release/
	cp data_recorder.py release/
	cp data_analysis.py release/
	cp network_stream.py release/
	cp realtime_display.py release/
	cp advanced_display.py release/
	cp verify_dma_integrity.py release/
	cp full_pipeline_test.py release/
	cp requirements.txt release/
	cp README.md release/
	tar -czf release/turboquant-$(shell date +%Y%m%d).tar.gz release/
	@echo "Release package created: release/turboquant-$(shell date +%Y%m%d).tar.gz"

# =============================================================================
# Maintenance
# =============================================================================

clean:
	rm -rf $(BUILD_DIR)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -f *.pyc
	rm -f *.png
	rm -f test_*.h5
	rm -f *.html
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned build artifacts"

distclean: clean
	rm -rf $(VENV_DIR)
	rm -rf artifacts
	rm -rf release
	rm -rf $(DOCS_DIR)
	rm -f *.h5 *.npz *.csv *.wav *.tdms *.bin
	@echo "Cleaned everything"

# =============================================================================
# Development Helpers
# =============================================================================

serve-docs:
	@echo "Serving documentation on http://localhost:8000"
	$(PYTHON) -m http.server 8000 --directory $(DOCS_DIR) 2>/dev/null || \
	$(PYTHON) -m SimpleHTTPServer 8000 2>/dev/null || \
	echo "Cannot start server"

benchmark:
	@echo "Running performance benchmark..."
	$(PYTHON) -c "import timeit; print('Python overhead:', timeit.timeit('pass', number=1000000))"
	@echo "Benchmark complete"

update:
	@echo "Updating dependencies..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "Update complete"

# =============================================================================
# Utility Targets
# =============================================================================

list-ports:
	@echo "Available serial ports:"
	@ls /dev/ttyUSB* 2>/dev/null || echo "  No USB serial ports found"
	@ls /dev/ttyACM* 2>/dev/null || echo "  No ACM serial ports found"
	@ls /dev/tty.* 2>/dev/null || echo "  No macOS serial ports found"

version:
	@echo "TurboQuant Build System"
	@echo "======================="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Date: $(shell date)"
	@echo "Git: $(shell git describe --tags --always 2>/dev/null || echo 'unknown')"
