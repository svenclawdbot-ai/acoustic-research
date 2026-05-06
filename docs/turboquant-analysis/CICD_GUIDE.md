# CI/CD and Build System Guide

Complete guide for the TurboQuant build system, CI/CD pipelines, and containerization.

---

## Build System (Make)

The `Makefile` provides a unified interface for all build tasks.

### Quick Reference

```bash
make help              # Show all available targets
make install           # Install Python dependencies
make firmware          # Build ESP32 firmware
make flash             # Flash firmware to device
make test              # Run test suite
make clean             # Clean build artifacts
```

### Common Workflows

#### Initial Setup
```bash
# Clone repository
git clone https://github.com/yourusername/turboquant.git
cd turboquant

# Install dependencies
make install

# Or use virtual environment
make venv
source .venv/bin/activate
make install
```

#### Firmware Development
```bash
# Build firmware
make firmware

# Flash and monitor
make flash
make monitor

# Combined build + flash
make fullflash

# Erase flash if needed
make erase
```

#### Software Development
```bash
# Check code quality
make check

# Run tests
make test

# Format code
make format

# Quick demo
make display
```

#### Data Operations
```bash
# Record test data
make acquire

# Analyze results
make analyze

# Start streaming
make stream
```

---

## CI/CD Pipeline (GitHub Actions)

The CI/CD pipeline is defined in `.github/workflows/ci-cd.yml`.

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                        CI/CD PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Python       │───▶│ Python       │───▶│ Firmware     │      │
│  │ Quality      │    │ Tests        │    │ Build        │      │
│  │ (black,      │    │ (pytest)     │    │ (ESP-IDF)    │      │
│  │  flake8)     │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │                │
│         └───────────────────┴───────────────────┘                │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │ Documentation    │                         │
│                    │ Build            │                         │
│                    └──────────────────┘                         │
│                              │                                   │
│                              ▼ (on tags)                         │
│                    ┌──────────────────┐                         │
│                    │ Release          │                         │
│                    │ Creation         │                         │
│                    └──────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Trigger Conditions

| Event | Actions Triggered |
|-------|-------------------|
| Push to `main` | Full CI + Docker build |
| Push to `develop` | Full CI |
| Pull Request | Python quality + tests |
| Tag `v*` | Full CI + Release creation |

### Jobs

#### 1. Python Quality
- **Tool:** black, flake8, pylint, mypy
- **Checks:**
  - Code formatting (black)
  - Style violations (flake8)
  - Static analysis (pylint)
  - Type checking (mypy)
- **Policy:** Fails on errors, warnings allowed

#### 2. Python Tests
- **Tool:** pytest
- **Tests:**
  - Import checks
  - Data recorder functionality
  - Data analysis functionality
  - Integration tests
- **Coverage:** Uploaded to Codecov

#### 3. Firmware Build
- **Tool:** ESP-IDF v5.0
- **Target:** ESP32-S3
- **Artifacts:** .bin, .elf, .map files
- **Caching:** ESP-IDF installation cached

#### 4. Documentation Build
- **Tool:** pydoc, mkdocs
- **Output:** HTML documentation
- **Artifacts:** docs/ directory

#### 5. Release (Tags Only)
- **Trigger:** Git tag matching `v*`
- **Actions:**
  - Creates GitHub Release
  - Uploads firmware binaries
  - Uploads Python package
  - Uploads documentation
- **Assets:**
  - `turboquant-vX.X.X.tar.gz`
  - `turboquant-vX.X.X.zip`

### Status Badges

Add to `README.md`:

```markdown
[![CI/CD](https://github.com/yourusername/turboquant/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/turboquant/actions)
[![codecov](https://codecov.io/gh/yourusername/turboquant/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/turboquant)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## Docker Containers

### Images

| Image | Purpose | Size |
|-------|---------|------|
| `turboquant:latest` | Production runtime | ~200MB |
| `turboquant:dev` | Development environment | ~500MB |
| `turboquant:analysis` | Data analysis only | ~300MB |
| `turboquant:firmware` | ESP-IDF build environment | ~2GB |

### Usage

#### Production
```bash
# Build production image
docker build --target production -t turboquant:latest .

# Run acquisition
docker run --rm --device /dev/ttyUSB0 \
    turboquant:latest acquire --duration 60

# Run display (requires X11)
docker run --rm -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    turboquant:latest display --mode demo
```

#### Development
```bash
# Build development image
docker build --target development -t turboquant:dev .

# Run interactive shell
docker run -it --rm -v $(pwd):/app turboquant:dev bash

# Run tests in container
docker run --rm turboquant:dev make test
```

#### Using Docker Compose

```bash
# Start streaming server
docker-compose up -d server

# Start client (GUI)
docker-compose --profile gui up client

# Start Jupyter notebook
docker-compose up notebook

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `server` | 5555/5556 | ZeroMQ streaming server |
| `client` | - | GUI client (requires X11) |
| `notebook` | 8888 | Jupyter analysis environment |
| `acquire` | - | Hardware acquisition (privileged) |
| `docs` | 8000 | Documentation server |

---

## Release Process

### Creating a Release

```bash
# 1. Update version
vim turboquant.py  # Update __version__

# 2. Commit changes
git add .
git commit -m "Prepare release v1.2.0"

# 3. Create tag
git tag -a v1.2.0 -m "Release version 1.2.0"

# 4. Push to trigger CI
git push origin main
git push origin v1.2.0
```

### Automated Release

The CI pipeline will:
1. Build all artifacts
2. Create GitHub Release
3. Upload binaries
4. Generate release notes

### Manual Release (if needed)

```bash
# Create release package
make ci-package

# Create GitHub release manually
gh release create v1.2.0 \
    --title "TurboQuant v1.2.0" \
    --notes "Release notes..." \
    release/*.tar.gz release/*.zip
```

---

## Development Workflow

### Branching Strategy

```
main     ─────●─────●─────●─────●─────
              ↑                     ↑
develop  ────┘─────●─────●─────┘
                    ↑     ↑
feature  ──────────┘     └───── feature/dma-optimization

hotfix   ─────────────────●───── (emergency fixes)
```

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `hotfix/*`: Emergency fixes

### Pull Request Process

1. Create feature branch
   ```bash
   git checkout -b feature/my-feature develop
   ```

2. Make changes and commit
   ```bash
   git add .
   git commit -m "Add feature X"
   ```

3. Push and create PR
   ```bash
   git push origin feature/my-feature
   # Create PR via GitHub UI
   ```

4. CI runs automatically
   - Python quality checks
   - Unit tests
   - Integration tests

5. Merge when CI passes

---

## Local CI Testing

Test CI locally before pushing:

```bash
# Install act (GitHub Actions local runner)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act push

# Run specific job
act -j python-quality

# Run with firmware build (requires ESP-IDF)
act -j firmware-build
```

---

## Troubleshooting

### CI Build Failures

#### Python Quality Failures
```bash
# Run locally to see issues
make check

# Auto-fix formatting
make format
```

#### Firmware Build Failures
```bash
# Check ESP-IDF installation
. ~/esp/esp-idf/export.sh
idf.py --version

# Clean and rebuild
idf.py fullclean
idf.py build
```

#### Docker Build Failures
```bash
# Build with verbose output
docker build --progress=plain -t turboquant:latest .

# Check layer caching
docker build --no-cache -t turboquant:latest .
```

### Common Issues

**"No space left on device" in CI:**
- Add cleanup step
- Use caching more aggressively
- Remove unnecessary packages

**"Permission denied" on serial device:**
- Add user to `dialout` group
- Use `sudo` for testing
- In Docker: run privileged

**ESP-IDF download timeout:**
- Use shallow clone: `--depth 1`
- Cache ESP-IDF directory
- Use pre-built image

---

## Files Reference

| File | Purpose |
|------|---------|
| `Makefile` | Build automation |
| `.github/workflows/ci-cd.yml` | GitHub Actions CI/CD |
| `Dockerfile` | Multi-stage container builds |
| `docker-compose.yml` | Development environment orchestration |
| `.gitignore` | Git ignore patterns |
| `requirements.txt` | Python dependencies |

---

## Best Practices

1. **Commit Messages:**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`
   - Reference issues: `Fixes #123`
   - Keep first line under 50 chars

2. **Versioning:**
   - Use semantic versioning (semver)
   - Tag format: `v1.2.3`
   - Pre-releases: `v1.2.3-alpha.1`

3. **Testing:**
   - Run `make test` before pushing
   - Add tests for new features
   - Maintain >80% coverage

4. **Documentation:**
   - Update README for user-facing changes
   - Update guides for architectural changes
   - Add docstrings to new functions

---

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [ESP-IDF CI Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/tools/idf-docker-image.html)
- [Makefile Tutorial](https://makefiletutorial.com/)
