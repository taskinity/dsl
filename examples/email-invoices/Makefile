.PHONY: help setup install test run clean

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
	@echo "  make run          - Run the email processor"
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
	$(PYTEST) tests/ -v --cov=email_processor --cov-report=term-missing

# Run code style checks
lint:
	$(FLAKE8 email_processor/
	$(BLACK) --check email_processor/ tests/
	$(ISORT) --check-only email_processor/ tests/

# Format the code
format:
	$(BLACK) email_processor/ tests/
	$(ISORT) email_processor/ tests/

# Run the email processor
run:
	$(PYTHON_VENV) process_invoices.py

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} \; || true
	find . -type d -name "*.egg-info" -exec rm -r {} \; || true
	find . -type d -name ".pytest_cache" -exec rm -r {} \; || true
	find . -type d -name ".mypy_cache" -exec rm -r {} \; || true
	docker-compose down -v || true

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
