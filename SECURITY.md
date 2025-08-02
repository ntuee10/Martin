# 🔐 MARTIN API KEY SECURITY GUIDE

## ✅ Current Security Status

**GOOD NEWS:** Your API keys are already protected!
- ✅ `.env` file is in `.gitignore` 
- ✅ No `.env` files tracked in git
- ✅ Backend code uses environment variables
- ✅ No hardcoded keys in source code

## 🛡️ Security Best Practices

### 1. **Never Commit .env Files**
```bash
# Always verify before pushing
git status
# Should NOT show any .env files

# If you accidentally staged .env:
git rm --cached backend/.env
git commit -m "Remove .env from tracking"
```

### 2. **Double-Check Before Pushing**
```bash
# Search for potential API keys in your code
grep -r "xai-" . --exclude-dir=node_modules --exclude-dir=venv --exclude=*.env
# Should return NOTHING

# Check git history for keys
git log -p | grep -i "api_key\|xai-"
# Should only show placeholders like "your_grok3_api_key_here"
```

### 3. **Use Environment Variables Only**
```python
# ✅ CORRECT - In your Python code
api_key = os.getenv("GROK3_API_KEY")

# ❌ WRONG - Never do this
api_key = "xai-actualKeyHere123"
```

### 4. **Secure Your Local .env File**
```bash
# Set restrictive permissions
chmod 600 backend/.env

# Only you can read/write
ls -la backend/.env
# Should show: -rw-------
```

### 5. **Use Different Keys for Different Environments**
```env
# Development (.env.development)
GROK3_API_KEY=xai-dev-key-with-limits

# Production (.env.production)
GROK3_API_KEY=xai-prod-key-with-higher-limits
```

## 🚨 If You Accidentally Exposed a Key

1. **Immediately revoke the key** at https://x.ai/api
2. **Generate a new key**
3. **Update your .env file**
4. **Check git history**:
   ```bash
   # If key is in history, you need to clean it
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch backend/.env" \
   --prune-empty --tag-name-filter cat -- --all
   ```

## 📋 Pre-Push Security Checklist

Before EVERY push to GitHub:

- [ ] Run: `git status` - No .env files should appear
- [ ] Run: `grep -r "xai-" .` - Should find NO real keys
- [ ] Check: `backend/.env` permissions are 600
- [ ] Verify: `.gitignore` includes `.env`
- [ ] Review: Changed files don't contain keys

## 🔒 Additional Security Measures

### 1. **Add Pre-commit Hook**
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Prevent commits with API keys

if git diff --cached --name-only | grep -E "\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    exit 1
fi

if git diff --cached | grep -E "xai-[a-zA-Z0-9]{20,}"; then
    echo "ERROR: Possible API key detected in commit!"
    echo "Remove the key and try again."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 2. **Use GitHub Secrets (for CI/CD)**
Instead of putting keys in code:
1. Go to GitHub repo → Settings → Secrets
2. Add `GROK3_API_KEY` as a repository secret
3. Use in GitHub Actions:
   ```yaml
   env:
     GROK3_API_KEY: ${{ secrets.GROK3_API_KEY }}
   ```

### 3. **Monitor for Exposed Keys**
- Enable GitHub secret scanning
- Use tools like GitGuardian
- Set up alerts for your key prefix

## 📝 Safe Sharing Instructions

When sharing Martin with others:

### Share the Code (Safe):
```bash
# This is safe - no keys included
git clone https://github.com/ntuee10/Martin.git
```

### Tell Users to Add Their Own Key:
```markdown
## Setup Instructions
1. Get your API key from https://x.ai/api
2. Copy `backend/.env.example` to `backend/.env`
3. Add your key: `GROK3_API_KEY=your-key-here`
```

## ⚡ Quick Security Commands

```bash
# Check if .env is ignored
git check-ignore backend/.env
# Output: backend/.env (means it's ignored ✅)

# See what will be committed
git diff --cached --name-only

# Verify no keys in history
git log --all --grep="xai-"

# Emergency: Remove all .env from history
git filter-repo --path backend/.env --invert-paths
```

## 🎯 Summary

Your setup is already secure! Just remember:
1. **Never** remove `.env` from `.gitignore`
2. **Always** check `git status` before pushing
3. **Only** share `.env.example`, never `.env`
4. **Revoke** keys immediately if exposed

The current setup ensures your API key stays private while allowing others to use their own keys with Martin.
