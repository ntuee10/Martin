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
    
    # Exclude known safe patterns: demo-token, placeholders, .env.example files
    if grep -r $exclude_dirs -iE "$pattern" . 2>/dev/null | \
       grep -v ".env.example" | \
       grep -v "your_.*_here" | \
       grep -v "placeholder" | \
       grep -v "demo-token" | \
       grep -v "test-token" | \
       grep -v "dummy" | \
       grep -v "example"; then
        echo -e "${RED}❌ FOUND${NC}"
        echo -e "${RED}   Potential secrets detected! Review the above matches.${NC}"
        ISSUES_FOUND=1
    else
        echo -e "${GREEN}✅ Clean${NC}"
    fi
}

# 1. Check git status for .env files (but not .env.example)
echo -n "Checking git status for .env files... "
if git status --porcelain | grep -E "\.env$" | grep -v "\.env\.example"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   .env files are staged for commit!${NC}"
    echo -e "${YELLOW}   Run: git rm --cached <filename>${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# 2. Check for Grok API keys
check_pattern "xai-[a-zA-Z0-9]{20,}" "Grok API keys (xai-...)"

# 3. Check for generic API key patterns (excluding demo tokens)
echo -n "Checking for API key patterns... "
if grep -r --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude=*.env --exclude=SECURITY.md \
   -iE "(api[_-]?key|apikey)[[:space:]]*[=:][[:space:]]*['\"]?[a-zA-Z0-9]{20,}" . 2>/dev/null | \
   grep -v "demo-token" | \
   grep -v "test-token" | \
   grep -v "your_.*_here" | \
   grep -v ".env.example"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   Potential API keys detected!${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# 4. Check for exposed secrets (excluding demo values)
echo -n "Checking for exposed secrets... "
if grep -r --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude=*.env --exclude=SECURITY.md \
   -iE "(secret|password)[[:space:]]*[=:][[:space:]]*['\"][^'\"]{10,}['\"]" . 2>/dev/null | \
   grep -v "your-secret-key-here" | \
   grep -v "demo" | \
   grep -v "example" | \
   grep -v "test" | \
   grep -v "placeholder"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   Potential secrets detected!${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

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
if git log --all -p | grep -E "xai-[a-zA-Z0-9]{20,}" | grep -v "your_grok3_api_key_here" | grep -v "xai-YOUR"; then
    echo -e "${RED}❌ FOUND${NC}"
    echo -e "${RED}   API keys found in git history!${NC}"
    echo -e "${RED}   This requires cleaning git history before pushing${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# 8. List all environment-like files
echo -n "Scanning for environment files... "
# Count actual .env files (not .env.example)
ENV_COUNT=0
TRACKED_ENV_COUNT=0

# Find .env files but exclude .env.example
for file in $(find . -name "*.env" -o -name ".env*" 2>/dev/null | grep -v node_modules | grep -v venv | grep -v ".env.example" | grep -v ".env.*.example"); do
    ENV_COUNT=$((ENV_COUNT + 1))
    if git ls-files --error-unmatch "$file" 2>/dev/null; then
        echo -e "${RED}❌ $file is tracked in git!${NC}"
        TRACKED_ENV_COUNT=$((TRACKED_ENV_COUNT + 1))
        ISSUES_FOUND=1
    fi
done

if [ $ENV_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ No .env files found${NC}"
elif [ $TRACKED_ENV_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ Found $ENV_COUNT .env file(s), none tracked${NC}"
else
    echo -e "${RED}❌ Found $TRACKED_ENV_COUNT .env file(s) in git!${NC}"
fi

# 9. Verify .env.example files exist (these SHOULD be in git)
echo -n "Checking for .env.example files... "
if [ -f "backend/.env.example" ]; then
    if git ls-files --error-unmatch "backend/.env.example" 2>/dev/null; then
        echo -e "${GREEN}✅ Properly tracked (template file)${NC}"
    else
        echo -e "${YELLOW}⚠️  Not in git (should be tracked)${NC}"
        echo -e "${YELLOW}   Run: git add backend/.env.example${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Missing .env.example${NC}"
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
    echo "  2. Never commit real .env files"
    echo "  3. .env.example files are safe to share"
    echo ""
    echo "Note: 'demo-token' in demo.py is intentional (not a real key)"
else
    echo -e "${RED}❌ SECURITY ISSUES DETECTED!${NC}"
    echo -e "${RED}   Fix the above issues before pushing${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  • Remove .env from git: git rm --cached <file>"
    echo "  • Set permissions: chmod 600 backend/.env"
    echo "  • Clean history: See SECURITY.md for instructions"
    exit 1
fi

echo ""
echo "📚 See SECURITY.md for detailed security guidelines"
