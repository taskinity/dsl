#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "./examples/email-invoices/.env" ]; then
    echo -e "${BLUE}Setting up test environment...${NC}"
    ./test_scripts/setup_test_environment.sh
fi

# Create necessary directories
mkdir -p ./output/email
mkdir -p ./logs/email

# Export environment variables from .env file
export $(grep -v '^#' ./examples/email-invoices/.env | xargs)

# Set default values if not set
export EMAIL_SERVER=${EMAIL_SERVER:-localhost}
export EMAIL_PORT=${EMAIL_PORT:-1025}
export EMAIL_USER=${EMAIL_USER:-test@example.com}
export EMAIL_PASSWORD=${EMAIL_PASSWORD:-testpass}
export OUTPUT_DIR=${OUTPUT_DIR:-./output/email}
export LOG_LEVEL=${LOG_LEVEL:-DEBUG}

# Start the mail server if not already running
if ! docker ps | grep -q mailhog; then
    echo -e "${BLUE}Starting mail server...${NC}"
    docker-compose up -d mailserver
    echo -e "${GREEN}Mail server is running at http://localhost:8025${NC}"
fi

# Load test emails if the mail server is empty
if [ "$(curl -s http://localhost:8025/api/v2/messages | jq '.count')" -eq 0 ]; then
    echo -e "${BLUE}Loading test emails...${NC}"
    ./test_scripts/load_test_emails.sh
fi

# Install the package in development mode
echo -e "${BLUE}Installing package in development mode...${NC}"
python -m pip install -e .

# Run the email processor
echo -e "${GREEN}Starting email processor...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"

exec python -m email_processor --config ./examples/email-invoices/process_invoices.yaml
