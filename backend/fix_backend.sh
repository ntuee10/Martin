# 1. Clean up and start fresh
cd Martin/backend
deactivate  # Exit current venv if active
rm -rf venv

# 2. Create new venv
python3 -m venv venv
source venv/bin/activate

# 3. Create minimal requirements.txt (copy from above)
cat > requirements.txt << 'EOF'
# Martin Backend Minimal Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
redis==5.0.1
httpx==0.25.2
python-dotenv==1.0.0
structlog==23.2.0
EOF

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Verify installation
python -c "import fastapi, httpx, redis; print('✅ All modules installed successfully')"

# 6. Run Martin
python martin_backend.py