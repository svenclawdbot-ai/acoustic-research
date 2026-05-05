# Dockerfile for TurboQuant
# Provides a containerized environment for development and deployment

FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libhdf5-dev \
    libffi-dev \
    libssl-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# =============================================================================
# Development stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install \
    pytest \
    pytest-cov \
    pytest-mock \
    black \
    flake8 \
    pylint \
    mypy \
    ipython \
    jupyter \
    matplotlib \
    pyqt5

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Set entrypoint for development
CMD ["bash"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as production

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY turboquant.py .
COPY data_recorder.py .
COPY data_analysis.py .
COPY network_stream.py .
COPY realtime_display.py .
COPY advanced_display.py .
COPY verify_dma_integrity.py .
COPY full_pipeline_test.py .
COPY *.md .

# Create non-root user
RUN useradd -m -u 1000 turboquant && \
    chown -R turboquant:turboquant /app
USER turboquant

# Expose port for streaming
EXPOSE 5555

# Default command
CMD ["python", "turboquant.py", "--help"]

# =============================================================================
# ESP-IDF stage (for firmware builds)
# =============================================================================
FROM espressif/idf:v5.0 as firmware

# Copy firmware source
WORKDIR /workspace
COPY . .

# Build firmware
RUN idf.py set-target esp32s3 && \
    idf.py build

# Copy build artifacts to output directory
RUN mkdir -p /output && \
    cp build/*.bin /output/ && \
    cp build/*.elf /output/ && \
    cp build/*.map /output/

# =============================================================================
# Analysis stage (for data processing)
# =============================================================================
FROM python:3.9-slim as analysis

WORKDIR /data

# Install analysis dependencies
RUN pip install \
    numpy \
    scipy \
    matplotlib \
    h5py \
    pandas \
    jupyter

# Copy analysis tools
COPY data_analysis.py /usr/local/bin/
COPY data_recorder.py /usr/local/bin/

# Make executable
RUN chmod +x /usr/local/bin/data_analysis.py

# Entry point for analysis
ENTRYPOINT ["python", "/usr/local/bin/data_analysis.py"]
CMD ["--help"]
