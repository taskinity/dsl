# Camel Router - Multi-language ML/Media Processing Pipeline
# Makefile for development and deployment

.PHONY: help install dev test clean build docker run-example lint docs

# Default target
help:
	@echo "Camel Router - Multi-language Processing Engine"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install the package and dependencies"
	@echo "  dev         - Install in development mode"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting and format checks"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build distribution packages"
	@echo "  docker      - Build Docker image"
	@echo "  run-example - Run example camera processing pipeline"
	@echo "  docs        - Generate documentation"
	@echo "  setup-env   - Create example .env file"

# Installation
install:
	pip install -e .
	@echo "✅ Camel Router installed"

dev: install
	pip install -e ".[dev]"
	@echo "✅ Development environment ready"

# Dependencies for different languages
install-deps:
	@echo "Installing dependencies for external processors..."
	# Python ML dependencies
	pip install ultralytics opencv-python numpy

	# Check if Go is installed
	@which go > /dev/null || (echo "❌ Go not found. Install from https://golang.org/dl/" && exit 1)
	@echo "✅ Go found: $$(go version)"

	# Check if Node.js is installed
	@which node > /dev/null || (echo "⚠️  Node.js not found. Install from https://nodejs.org/")
	@which node > /dev/null && echo "✅ Node.js found: $$(node --version)"

	# Check if Rust is installed
	@which cargo > /dev/null || (echo "⚠️  Rust not found. Install from https://rustup.rs/")
	@which cargo > /dev/null && echo "✅ Rust found: $$(cargo --version)"

# Development
test:
	python -m pytest tests/ -v
	@echo "✅ Tests completed"

lint:
	python -m flake8 camel_router/
	python -m black --check camel_router/
	@echo "✅ Linting completed"

format:
	python -m black camel_router/
	@echo "✅ Code formatted"

# Build
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "✅ Cleaned build artifacts"

build: clean
	python setup.py sdist bdist_wheel
	@echo "✅ Distribution packages built"

# Docker
docker:
	docker build -t camel-router:latest .
	@echo "✅ Docker image built: camel-router:latest"

docker-run: docker
	docker run -it --rm \
		-v $(PWD)/examples:/app/examples \
		-v $(PWD)/.env:/app/.env \
		camel-router:latest \
		camel-router run -c examples/simple_routes.yaml

# Examples and setup
setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "📝 Please edit .env with your configuration"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

init-camera:
	camel-router init --template camera --output camera_routes.yaml
	@echo "✅ Camera configuration template created"
	@echo "📝 Edit camera_routes.yaml and run: make run-camera"

init-grpc:
	camel-router init --template grpc --output grpc_routes.yaml
	@echo "✅ gRPC configuration template created"

run-example: setup-env
	@echo "🚀 Running camera detection example..."
	camel-router run -c examples/simple_routes.yaml --verbose

run-camera: setup-env
	@echo "🚀 Running camera processing pipeline..."
	camel-router run -c camera_routes.yaml --route smart_camera_detection --verbose

run-health:
	@echo "🚀 Running health check pipeline..."
	camel-router run -c examples/simple_routes.yaml --route system_health_check --verbose

validate:
	camel-router validate -c examples/simple_routes.yaml
	@echo "✅ Configuration validated"

dry-run:
	camel-router run -c examples/simple_routes.yaml --dry-run
	@echo "✅ Dry run completed"

# External processor compilation
build-go:
	@echo "🔨 Building Go processors..."
	cd scripts && go mod init camel-processors || true
	cd scripts && go mod tidy || true
	cd scripts && go build -o ../bin/image_processor image_processor.go
	cd scripts && go build -o ../bin/health_check health_check.go
	@echo "✅ Go processors built in bin/"

build-cpp:
	@echo "🔨 Building C++ processors (if available)..."
	@if [ -f scripts/cpp_processor.cpp ]; then \
		mkdir -p bin; \
		g++ -O3 -o bin/cpp_postprocessor scripts/cpp_processor.cpp; \
		echo "✅ C++ processor built"; \
	else \
		echo "⚠️  No C++ processor found"; \
	fi

build-rust:
	@echo "🔨 Building Rust processors (if available)..."
	@if [ -f scripts/Cargo.toml ]; then \
		cd scripts && cargo build --release; \
		cp scripts/target/release/* bin/ 2>/dev/null || true; \
		echo "✅ Rust processors built"; \
	else \
		echo "⚠️  No Rust processor found"; \
	fi

build-all: build-go build-cpp build-rust
	@echo "✅ All external processors built"

# Monitoring and debugging
logs:
	tail -f alerts/*.log

monitor:
	@echo "📊 Starting monitoring dashboard..."
	python -c "
import http.server
import socketserver
import webbrowser
import os

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

os.chdir('monitoring')
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Monitoring dashboard at http://localhost:{PORT}')
    webbrowser.open(f'http://localhost:{PORT}')
    httpd.serve_forever()
"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	mkdir -p docs
	python -c "
import camel_router
help(camel_router)
" > docs/api.md
	@echo "✅ Documentation generated in docs/"

# Deployment helpers
deploy-docker:
	docker tag camel-router:latest your-registry.com/camel-router:latest
	docker push your-registry.com/camel-router:latest
	@echo "✅ Docker image deployed"

deploy-k8s:
	kubectl apply -f k8s/
	@echo "✅ Deployed to Kubernetes"

# Performance testing
benchmark:
	@echo "🏃 Running performance benchmarks..."
	python scripts/benchmark.py
	@echo "✅ Benchmarks completed"

# Quick start for new users
quickstart: install-deps setup-env init-camera build-go
	@echo ""
	@echo "🎉 Camel Router Quick Start Complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your camera and email settings"
	@echo "2. Run: make run-camera"
	@echo "3. Check the logs and alerts/"
	@echo ""
	@echo "For more examples: make run-example"
	@echo "For validation: make validate"

# Development workflow
dev-workflow: dev lint test build
	@echo "✅ Development workflow completed"