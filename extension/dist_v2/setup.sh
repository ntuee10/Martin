#!/bin/bash

# Martin v2.0 Setup Script
echo "🚀 Setting up Martin v2.0..."
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if command_exists python3; then
    PYTHON_CMD=python3
elif command_exists python; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python found: $($PYTHON_CMD --version)${NC}"

# Setup backend
echo -e "\n${BLUE}Setting up backend...${NC}"
cd ../../backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "\n${BLUE}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit backend/.env and add your GROK3_API_KEY${NC}"
fi

# Create icons if they don't exist
echo -e "\n${BLUE}Creating extension icons...${NC}"
cd ../extension/dist_v2/icons

# Create simple SVG icons
for size in 16 48 128; do
    if [ ! -f "icon${size}.png" ]; then
        echo "Creating icon${size}.png..."
        cat > icon${size}.svg << EOF
<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="24" height="24" rx="4" fill="#3B82F6"/>
  <path d="M12 5L6 8.5L12 12L18 8.5L12 5Z" fill="white"/>
  <path d="M6 15.5L12 19L18 15.5" stroke="white" stroke-width="2"/>
  <path d="M6 11.5L12 15L18 11.5" stroke="white" stroke-width="2"/>
</svg>
EOF
        # Note: In production, use a proper SVG to PNG converter
        echo "  Note: Please convert icon${size}.svg to PNG format"
    fi
done

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Add your GROK3_API_KEY to backend/.env"
echo "2. Convert SVG icons to PNG format"
echo "3. Run the backend: cd backend && python martin_grok3_v2.py"
echo "4. Load the extension in Chrome from extension/dist_v2"
echo -e "\n${GREEN}Happy prompting with Martin! 🚀${NC}"
