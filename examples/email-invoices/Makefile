.PHONY: help setup install test run clean lint format typecheck dev-requirements

# Project variables
PROJECT_NAME = email-invoice-processor
PYTHON = python3
PIP = pip3
VENV = venv
PYTHON_VENV = $(VENV)/bin/python
PIP_VENV = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
FLAKE8 = $(VENV)/bin/flake8
BLACK = $(VENV)/bin/black
ISORT = $(VENV)/bin/isort
MYPY = $(VENV)/bin/mypy

# Help message
help:
	@echo "\n\033[1m$(PROJECT_NAME) - Makefile Help\033[0m"
	@echo "\nAvailable targets:"
	@echo "  make help         - Show this help message"
	@echo "  make setup        - Set up the development environment"
	@echo "  make install      - Install the package in development mode"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run code style checks"
	@echo "  make typecheck    - Run type checking"
	@echo "  make format       - Format the code"
	@echo "  make run          - Run the email processor"
	@echo "  make clean        - Clean up temporary files"

# Setup development environment
setup: venv requirements-dev.txt
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

# Install the package in development mode
install:
	$(PIP_VENV) install -e .

# Run tests
test:
	$(PYTEST) tests/ -v --cov=email_processor --cov-report=term-missing

# Run code style checks
lint:
	$(FLAKE8) email_processor tests
	$(BLACK) --check email_processor tests
	$(ISORT) --check-only email_processor tests

# Run type checking
typecheck:
	$(MYPY) email_processor

# Format the code
format:
	$(BLACK) email_processor tests
	$(ISORT) email_processor tests

# Run the email processor
run:
	$(PYTHON) -m email_processor --config process_invoices.yaml

# Stop Docker containers and remove volumes
stop:
	@echo "Stopping all Docker containers and removing volumes..."
	@docker-compose -f ../docker-compose.yml down -v --remove-orphans || true
	@echo "✅ All Docker containers stopped and volumes removed"

# Clean up
clean: stop
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +

# Generate development requirements
dev-requirements: requirements-dev.txt

requirements-dev.txt: requirements.txt
	echo "-r requirements.txt" > requirements-dev.txt
	echo "\n# Development dependencies" >> requirements-dev.txt
	echo "pytest==7.4.0" >> requirements-dev.txt
	echo "pytest-cov==4.1.0" >> requirements-dev.txt
	echo "flake8==6.1.0" >> requirements-dev.txt
	echo "black==23.7.0" >> requirements-dev.txt
	echo "isort==5.12.0" >> requirements-dev.txt
	echo "mypy==1.5.0" >> requirements-dev.txt
	echo "types-requests==2.31.0.1" >> requirements-dev.txt

# Default target
.DEFAULT_GOAL := help
