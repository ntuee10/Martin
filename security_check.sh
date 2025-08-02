#!/bin/bash

# Martin Security Check Script
# Run this before pushing to GitHub to ensure no secrets are exposed

echo "🔐 Martin Security Pre-Push Check"
echo "================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any issues found
ISSUES_FOUND=0

# Function to check for patterns
check_pattern() {
    local pattern=$1
    local description=$2
    local exclude_dirs="--exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude=*.env --exclude=SECURITY.md"
    
    echo -n "Checking for $description... "
    
    if grep -r $exclude_dirs -iE "$pattern" . 2>/dev/null | grep -v ".env.example" | grep -v "your_.*_here" | grep -v "placeholder"; then
        echo -e "${RED}❌ FOUND${NC}"
        echo -e "${RED}   Potential secrets detected! Review the above matches.${NC}"
        ISSUES_FOUND=1
    else
        echo -e "${GREEN}✅ Clean${NC}"
    fi
}

# 1. Check git status for .env files
echo -n "Checking git status for .env files... "
if git status --porcelain | grep -E "\.env"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   .env files are staged for commit!${NC}"
    echo -e "${YELLOW}   Run: git rm --cached <filename>${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# 2. Check for Grok API keys
check_pattern "xai-[a-zA-Z0-9]{20,}" "Grok API keys (xai-...)"

# 3. Check for generic API key patterns
check_pattern "(api[_-]?key|apikey)[[:space:]]*[=:][[:space:]]*['\"]?[a-zA-Z0-9]{20,}" "API key patterns"

# 4. Check for exposed secrets
check_pattern "(secret|password|token)[[:space:]]*[=:][[:space:]]*['\"][^'\"]{10,}['\"]" "exposed secrets"

# 5. Verify .gitignore includes .env
echo -n "Checking .gitignore for .env entries... "
if grep -q "^\.env" .gitignore && grep -q "backend/\.env" .gitignore; then
    echo -e "${GREEN}✅ Properly configured${NC}"
else
    echo -e "${YELLOW}⚠️  Missing entries${NC}"
    echo -e "${YELLOW}   Ensure .gitignore includes: .env and backend/.env${NC}"
fi

# 6. Check file permissions on .env
echo -n "Checking .env file permissions... "
if [ -f "backend/.env" ]; then
    PERMS=$(stat -f "%OLp" backend/.env 2>/dev/null || stat -c "%a" backend/.env 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo -e "${GREEN}✅ Secure (600)${NC}"
    else
        echo -e "${YELLOW}⚠️  Permissions: $PERMS${NC}"
        echo -e "${YELLOW}   Run: chmod 600 backend/.env${NC}"
    fi
else
    echo -e "${GREEN}✅ No .env file found${NC}"
fi

# 7. Check git history for keys
echo -n "Checking git history for exposed keys... "
if git log --all -p | grep -E "xai-[a-zA-Z0-9]{20,}" | grep -v "your_grok3_api_key_here"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   API keys found in git history!${NC}"
    echo -e "${RED}   This requires cleaning git history before pushing${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# 8. List all environment-like files
echo -n "Scanning for all .env type files... "
ENV_FILES=$(find . -name "*.env" -o -name ".env*" -o -name "env.*" 2>/dev/null | grep -v node_modules | grep -v venv)
if [ -z "$ENV_FILES" ]; then
    echo -e "${GREEN}✅ None found${NC}"
else
    echo -e "${YELLOW}Found:${NC}"
    echo "$ENV_FILES" | while read -r file; do
        if git ls-files --error-unmatch "$file" 2>/dev/null; then
            echo -e "  ${RED}❌ $file (TRACKED IN GIT!)${NC}"
            ISSUES_FOUND=1
        else
            echo -e "  ${GREEN}✅ $file (not in git)${NC}"
        fi
    done
fi

echo ""
echo "================================="

# Final summary
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SECURITY CHECKS PASSED!${NC}"
    echo -e "${GREEN}   Safe to push to GitHub${NC}"
    echo ""
    echo "Remember to:"
    echo "  1. Keep your API key in backend/.env only"
    echo "  2. Never commit .env files"
    echo "  3. Use .env.example for documentation"
else
    echo -e "${RED}❌ SECURITY ISSUES DETECTED!${NC}"
    echo -e "${RED}   Fix the above issues before pushing${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  • Remove .env from git: git rm --cached backend/.env"
    echo "  • Update .gitignore: Add '.env' and 'backend/.env'"
    echo "  • Clean history: See SECURITY.md for instructions"
    exit 1
fi

echo ""
echo "📚 See SECURITY.md for detailed security guidelines"
