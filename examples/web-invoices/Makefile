.PHONY: help setup install test run clean providers

# Project variables
PROJECT_NAME = web-invoice-processor
PYTHON = python3
PIP = pip3
VENV = venv
PYTHON_VENV = $(VENV)/bin/python
PIP_VENV = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
FLAKE8 = $(VENV)/bin/flake8
BLACK = $(VENV)/bin/black
ISORT = $(VENV)/bin/isort

# Help message
help:
	@echo "\n\033[1m$(PROJECT_NAME) - Makefile Help\033[0m"
	@echo "\nAvailable targets:"
	@echo "  make help         - Show this help message"
	@echo "  make setup        - Set up the development environment"
	@echo "  make install      - Install the package in development mode"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run code style checks"
	@echo "  make format       - Format the code"
	@echo "  make run          - Run the web invoice processor"
	@echo "  make providers    - List available providers"
	@echo "  make clean        - Clean up temporary files"

# Setup development environment
setup: venv
	$(PIP_VENV) install -U pip setuptools wheel
	$(PIP_VENV) install -r requirements-dev.txt
	$(PIP_VENV) install -e .

# Create virtual environment
venv:
	if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV) && \
		. $(VENV)/bin/activate && \
		$(PIP) install --upgrade pip; \
	fi

# Install the package
install:
	$(PIP_VENV) install -e .

# Run tests
test:
	$(PYTEST) tests/ -v --cov=web_invoice_processor --cov-report=term-missing

# Run code style checks
lint:
	$(FLAKE8) web_invoice_processor/ providers/ tests/
	$(BLACK) --check web_invoice_processor/ providers/ tests/
	$(ISORT) --check-only web_invoice_processor/ providers/ tests/

# Format the code
format:
	$(BLACK) web_invoice_processor/ providers/ tests/
	$(ISORT) web_invoice_processor/ providers/ tests/

# Run the web invoice processor
run:
	$(PYTHON_VENV) web_invoice_processor.py

# List available providers
providers:
	@echo "\n\033[1mAvailable providers:\033[0m"
	@ls -1 providers/ | grep -v "__" | sed 's/\.py//' | sed 's/^/  - /'

# Stop Docker containers and remove volumes
stop:
	@echo "Stopping all Docker containers and removing volumes..."
	@if [ -f "../docker-compose.yml" ]; then \
		docker-compose -f ../docker-compose.yml down -v --remove-orphans || true; \
		echo "✅ All Docker containers stopped and volumes removed"; \
	else \
		echo "ℹ️  No docker-compose.yml found in parent directory"; \
	fi

# Clean up
clean: stop
	find . -type d -name "__pycache__" -exec rm -r {} \; || true
	find . -type d -name "*.egg-info" -exec rm -r {} \; || true
	find . -type d -name ".pytest_cache" -exec rm -r {} \; || true
	find . -type d -name ".mypy_cache" -exec rm -r {} \; || true

dev-requirements: requirements-dev.txt

requirements-dev.txt: requirements.txt
	echo "-r requirements.txt" > requirements-dev.txt
	echo "\n# Development dependencies" >> requirements-dev.txt
	echo "pytest==7.4.0" >> requirements-dev.txt
	echo "pytest-cov==4.1.0" >> requirements-dev.txt
	echo "pytest-mock==3.11.1" >> requirements-dev.txt
	echo "flake8==6.1.0" >> requirements-dev.txt
	echo "black==23.7.0" >> requirements-dev.txt
	echo "isort==5.12.0" >> requirements-dev.txt
	echo "mypy==1.5.0" >> requirements-dev.txt
	echo "types-requests==2.31.0.1" >> requirements-dev.txt

# Default target
.DEFAULT_GOAL := help
