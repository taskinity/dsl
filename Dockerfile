# Multi-stage Docker build for DialogChain
# Supports Python, Go, and other language processors for dialog processing

FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Go
FROM base as go-builder
RUN wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz && \
    rm go1.21.0.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

# Install Node.js
FROM go-builder as node-builder
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Install Rust (optional)
FROM node-builder as rust-builder
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Final application stage
FROM rust-builder as app

WORKDIR /app

# Copy Python package
COPY setup.py .
COPY dialogchain/ ./dialogchain/
COPY scripts/ ./scripts/
COPY examples/ ./examples/

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    numpy \
    scipy \
    pillow

# Build external processors
RUN mkdir -p bin

# Build Go processors
WORKDIR /app/scripts
RUN go mod init camel-processors || true
RUN go mod tidy || true
RUN go build -o ../bin/image_processor image_processor.go
RUN go build -o ../bin/health_check health_check.go

# Build Rust processors (if available)
RUN if [ -f Cargo.toml ]; then \
        cargo build --release && \
        cp target/release/* ../bin/ 2>/dev/null || true; \
    fi

WORKDIR /app

# Create directories for logs and output
RUN mkdir -p alerts logs results monitoring

# Set executable permissions
RUN chmod +x bin/* scripts/*.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["camel-router", "run", "-c", "examples/simple_routes.yaml", "--verbose"]

# Multi-architecture build support
# To build: docker buildx build --platform linux/amd64,linux/arm64 -t camel-router:latest .

# Development variant
FROM app as dev
RUN pip install --no-cache-dir \
    pytest \
    black \
    flake8 \
    jupyter \
    matplotlib \
    seaborn

# Add development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    tmux \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]

# Production optimized variant
FROM app as prod

# Remove build dependencies to reduce size
RUN apt-get remove -y \
    build-essential \
    wget \
    curl \
    git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Run as non-root user
RUN useradd -m -u 1000 camelrouter
RUN chown -R camelrouter:camelrouter /app
USER camelrouter

# Production startup
CMD ["camel-router", "run", "-c", "examples/simple_routes.yaml"]