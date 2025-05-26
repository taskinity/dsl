# Camel Router - Multi-language ML/Media Processing Pipeline
# Makefile for development and deployment

.PHONY: help install dev test clean build docker run-example lint docs \
        test-unit test-integration test-e2e coverage typecheck format check-codestyle \
        check-all pre-commit-install setup-dev-env docs-serve docs-clean

# Default target
help:
	@echo "Camel Router - Multi-language Processing Engine"
	@echo ""
	@echo "Available commands:"
	@echo "  install          - Install the package and dependencies"
	@echo "  dev              - Install in development mode"
	@echo "  test             - Run tests"
	@echo "  lint             - Run linting and format checks"
	@echo "  clean            - Clean build artifacts"
	@echo "  build            - Build distribution packages"
	@echo "  docker           - Build Docker image"
	@echo "  run-example      - Run an example (use EXAMPLE=name)"
	@echo "  list-examples    - List available examples"
	@echo "  view-logs        - View logs for running example"
	@echo "  stop-example     - Stop a running example"
	@echo "  docs             - Generate documentation"
	@echo "  setup-env        - Create example .env file"

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

# List available examples
list-examples:
	@echo "Available examples:"
	@echo "  simple  - Basic routing example"
	@echo "  grpc    - gRPC service integration"
	@echo "  iot     - IoT device communication"
	@echo "  camera  - Video processing pipeline"

# Initialize example configurations
init-camera:
	camel-router init --template camera --output examples/camera_routes.yaml
	@echo "✅ Camera configuration template created"

init-grpc:
	camel-router init --template grpc --output examples/grpc_routes.yaml
	@echo "✅ gRPC configuration template created"

init-iot:
	camel-router init --template iot --output examples/iot_routes.yaml
	@echo "✅ IoT configuration template created"

# Run examples
run-example: setup-env
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Error: Please specify an example with EXAMPLE=name"; \
		echo "Available examples: simple, grpc, iot, camera"; \
		exit 1; \
	fi
	@echo "🚀 Starting $(EXAMPLE) example..."
	@case "$(EXAMPLE)" in \
		simple) \
			python -m src.camel_router.cli --config examples/simple_routes.yaml ;; \
		grpc) \
			docker-compose -f examples/docker-compose.yml up -d grpc-server && \
			python -m src.camel_router.cli --config examples/grpc_routes.yaml ;; \
		iot) \
			docker-compose -f examples/docker-compose.yml up -d mosquitto && \
			python -m src.camel_router.cli --config examples/iot_routes.yaml ;; \
		camera) \
			python -m src.camel_router.cli --config examples/camera_routes.yaml ;; \
		*) \
			echo "Error: Unknown example '$(EXAMPLE)'"; \
			exit 1 ;; \
	esac

# View logs for running example
view-logs:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Error: Please specify an example with EXAMPLE=name"; \
		echo "Available examples: simple, grpc, iot, camera"; \
		exit 1; \
	fi
	@case "$(EXAMPLE)" in \
		grpc|iot) \
			docker-compose -f examples/docker-compose.yml logs -f ;; \
		*) \
			tail -f logs/camel_router.log ;; \
	esac

# Stop a running example
stop-example:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Error: Please specify an example with EXAMPLE=name"; \
		echo "Available examples: simple, grpc, iot, camera"; \
		exit 1; \
	fi
	@case "$(EXAMPLE)" in \
		grpc|iot) \
			docker-compose -f examples/docker-compose.yml down ;; \
		*) \
			echo "Example '$(EXAMPLE)' runs in the foreground. Use Ctrl+C to stop." ;; \
	esac

# Alias for backward compatibility
run-camera: setup-env
	@echo "🚀 Running camera processing pipeline..."
	@make run-example EXAMPLE=camera

run-grpc: setup-env
	@echo "🚀 Running gRPC example..."
	@make run-example EXAMPLE=grpc

run-iot: setup-env
	@echo "🚀 Running IoT example..."
	@make run-example EXAMPLE=iot

run-simple: setup-env
	@echo "🚀 Running simple example..."
	@make run-example EXAMPLE=simple

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
	python -c "\
import http.server\
import socketserver\
import webbrowser\
import os\
\
PORT = 8080\
Handler = http.server.SimpleHTTPRequestHandler\
\
os.chdir('monitoring')\
with socketserver.TCPServer(('', PORT), Handler) as httpd:\
    print(f'Monitoring dashboard at http://localhost:{PORT}')\
    webbrowser.open(f'http://localhost:{PORT}')\
    httpd.serve_forever()\
"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@mkdir -p docs
	@echo "import camel_router\nhelp(camel_router)" | python > docs/api.md
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