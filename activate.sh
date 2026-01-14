#!/bin/bash

# Activate script for ENS Deed Release Tool
# Usage: source activate.sh or . activate.sh

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display banner
show_banner() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${GREEN}ENS Deed Release Tool Environment${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
    echo ""
fi

# Display banner
show_banner

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Display Python version and location
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""
echo -e "Python version: ${YELLOW}$(python --version)${NC}"
echo -e "Python location: ${YELLOW}$(which python)${NC}"
echo -e "Pip version: ${YELLOW}$(pip --version)${NC}"
echo ""

# Check if requirements are installed
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Checking dependencies...${NC}"
    pip list --format=columns | grep -E "(web3|eth-account)" || {
        echo -e "${YELLOW}Dependencies not installed. Run: pip install -r requirements.txt${NC}"
        echo ""
    }
fi

# Display helpful commands
echo -e "${BLUE}Available commands:${NC}"
echo "  python check_deeds.py          - Check your deed status (view-only)"
echo "  python release_ens_deeds.py    - Release deeds and recover ETH"
echo "  pip install -r requirements.txt - Install dependencies"
echo "  deactivate                     - Exit virtual environment"
echo ""
echo -e "${GREEN}Ready to use ENS Deed Release Tool!${NC}"
echo ""