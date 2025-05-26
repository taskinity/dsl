#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}docker-compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

# Check if required tools are installed
if ! command -v swaks &> /dev/null; then
    echo -e "${YELLOW}swaks is not installed. Test emails cannot be sent.${NC}"
    echo "Install it with: sudo apt-get install swaks"
    echo -e "${YELLOW}Continuing without sending test emails...${NC}"
    SWAKS_INSTALLED=false
else
    SWAKS_INSTALLED=true
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}jq is not installed. Some checks will be limited.${NC}"
    echo "Install it with: sudo apt-get install jq"
    JQ_INSTALLED=false
else
    JQ_INSTALLED=true
fi

# Check if required services are running
echo -e "${GREEN}Checking required services...${NC}"

# Check MailHog
if ! docker ps | grep -q mailhog; then
    echo -e "${YELLOW}MailHog is not running. Starting it now...${NC}"
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d mailserver
    elif [ -f "../docker-compose.yml" ]; then
        docker-compose -f ../docker-compose.yml up -d mailserver
    else
        echo -e "${RED}Error: Could not find docker-compose.yml${NC}"
        exit 1
    fi
    sleep 2  # Give it a moment to start
fi

# Check Email Processor
if ! docker ps | grep -q email-invoice-processor; then
    echo -e "${YELLOW}Email Processor is not running. Starting it now...${NC}"
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d email-processor
    elif [ -f "../docker-compose.yml" ]; then
        docker-compose -f ../docker-compose.yml up -d email-processor
    else
        echo -e "${RED}Error: Could not find docker-compose.yml${NC}"
        exit 1
    fi
    sleep 2  # Give it a moment to start
fi

# Verify services
services_running=true

# Check MailHog status
if ! curl -s http://localhost:8025 > /dev/null; then
    echo -e "${RED}MailHog is not accessible at http://localhost:8025${NC}"
    services_running=false
else
    echo -e "${GREEN}✓ MailHog is running at http://localhost:8025${NC}"
fi

# Check Email Processor logs for errors
processor_logs=$(docker logs email-invoice-processor 2>&1 | tail -n 10)
if echo "$processor_logs" | grep -q -i "error\|exception"; then
    echo -e "${YELLOW}⚠  Email Processor has errors in logs:${NC}"
    echo "$processor_logs" | grep -i "error\|exception" | tail -n 5
    services_running=false
else
    echo -e "${GREEN}✓ Email Processor is running${NC}"
fi

# Check if test emails are loaded
if [ "$JQ_INSTALLED" = true ]; then
    email_count=$(curl -s http://localhost:8025/api/v2/messages | jq '.count' 2>/dev/null || echo "0")
    if [ "$email_count" -eq 0 ]; then
        echo -e "${YELLOW}No test emails found.${NC}"
        if [ "$SWAKS_INSTALLED" = true ] && [ -f "./test_scripts/load_test_emails.sh" ]; then
            echo -e "${YELLOW}Loading test emails...${NC}"
            ./test_scripts/load_test_emails.sh
        else
            echo -e "${YELLOW}Skipping test email loading (swaks not installed or script not found)${NC}"
        fi
    else
        echo -e "${GREEN}✓ $email_count test emails are loaded${NC}"
    fi
else
    echo -e "${YELLOW}jq not installed. Skipping email count check.${NC}"
fi

# Final status
if [ "$services_running" = true ]; then
    echo -e "\n${GREEN}✅ All services are running correctly!${NC}"
    echo -e "\nYou can now access:\n"
    echo -e "  • MailHog Web UI: ${GREEN}http://localhost:8025${NC}"
    echo -e "  • Email Processor Logs: ${GREEN}docker logs -f email-invoice-processor${NC}"
    echo -e "\nTo process emails, run: ${GREEN}./test_scripts/load_test_emails.sh${NC}"
else
    echo -e "\n${RED}❌ Some services are not running correctly. Please check the logs above.${NC}"
    exit 1
fi
