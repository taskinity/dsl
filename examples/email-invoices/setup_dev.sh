#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
PYTHON_VER=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
PYTHON_VER_NUM=$(python3 -c 'import sys; print("{:d}{:02d}".format(sys.version_info.major, sys.version_info.minor))')
if (( PYTHON_VER_NUM < 308 )); then
    echo -e "${RED}Python 3.8 or higher is required. Found Python $PYTHON_VER${NC}
    Please install Python 3.8 or higher and try again.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
echo -e "${GREEN}Upgrading pip and setuptools...${NC}"
pip install --upgrade pip setuptools wheel

# Install the package in development mode
echo -e "${GREEN}Installing the package in development mode...${NC}"
pip install -e .[dev]

# Install pre-commit hooks if pre-commit is installed
if command_exists pre-commit; then
    echo -e "${GREEN}Setting up pre-commit hooks...${NC}"
    pre-commit install
else
    echo -e "${YELLOW}pre-commit not installed. Skipping pre-commit setup.${NC}"
    echo "Install it with: pip install pre-commit"
fi

# Create necessary directories
mkdir -p logs output/test_emails

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cat > .env << 'EOL'
# Email Server Configuration
EMAIL_SERVER=localhost
EMAIL_PORT=1025
EMAIL_USER=test@example.com
EMAIL_PASSWORD=testpass
EMAIL_FOLDER=INBOX

# Processing Settings
PROCESSED_FOLDER=Processed
ERROR_FOLDER=Errors
OUTPUT_DIR=./output
LOG_LEVEL=INFO

# OCR Settings
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGES=eng,pol
EOL
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Check if Docker is running
if command_exists docker; then
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}Docker is running${NC}"
        
        # Check if docker-compose is installed
        if command_exists docker-compose; then
            echo -e "${GREEN}docker-compose is installed${NC}"
        else
            echo -e "${YELLOW}docker-compose is not installed. Install it with:${NC}"
            echo "  Linux: sudo apt-get install docker-compose-plugin"
            echo "  macOS: brew install docker-compose"
        fi
    else
        echo -e "${YELLOW}Docker is not running. Please start Docker and run this script again.${NC}"
    fi
else
    echo -e "${YELLOW}Docker is not installed. Install it from https://docs.docker.com/get-docker/${NC}"
fi

echo -e "\n${GREEN}✅ Development environment setup complete!${NC}"
echo -e "\nTo activate the virtual environment, run: ${GREEN}source venv/bin/activate${NC}"
echo -e "To run tests: ${GREEN}make test${NC}"
echo -e "To run the email processor: ${GREEN}make run${NC}"
echo -e "To start the development environment with Docker: ${GREEN}docker-compose up -d${NC}"
