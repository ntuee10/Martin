#!/bin/bash
# Martin Quick Setup - Run these commands to create the project

# Create directory structure
mkdir -p Martin/backend Martin/extension/src Martin/extension/public/icons
cd Martin

# Create backend files
cd backend

# Create .env.example
cat > .env.example << 'EOF'
# Grok 3 API Configuration
GROK3_API_KEY=your_grok3_api_key_here
GROK3_API_URL=https://api.x.ai/v1

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# Security
JWT_SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=["chrome-extension://*", "http://localhost:3000"]

# Monitoring
ENABLE_METRICS=true
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
redis==5.0.1
numpy==1.24.3
httpx==0.25.2
prometheus-client==0.19.0
structlog==23.2.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
ruff==0.1.6
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  martin-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - GROK3_API_KEY=${GROK3_API_KEY}
      - ENVIRONMENT=development
    depends_on:
      - redis
    volumes:
      - .:/app
    command: python martin_backend.py

volumes:
  redis_data:
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 martin && chown -R martin:martin /app
USER martin

EXPOSE 8000

CMD ["python", "martin_backend.py"]
EOF

# Create the main martin_backend.py file
echo "Creating martin_backend.py..."
# [The full martin_backend.py code from the previous artifact would go here]
# For brevity, I'll just show you need to copy it from the previous response

# Create extension files
cd ../extension

# Create package.json
cat > package.json << 'EOF'
{
  "name": "martin-extension",
  "version": "1.0.0",
  "description": "AI-powered prompt optimization for developers",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "zip": "npm run build && zip -r martin.zip dist/"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lodash": "^4.17.21",
    "zustand": "^4.4.0",
    "lucide-react": "^0.263.1"
  },
  "devDependencies": {
    "@types/chrome": "^0.0.251",
    "@types/lodash": "^4.14.201",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "prettier": "^3.1.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "vitest": "^1.0.0",
    "@types/node": "^20.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  }
}
EOF

# Create manifest.json
cat > manifest.json << 'EOF'
{
  "manifest_version": 3,
  "name": "Martin - AI Prompt Optimizer",
  "description": "Real-time prompt optimization for developers using AI",
  "version": "1.0.0",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "permissions": [
    "activeTab",
    "storage",
    "contextMenus"
  ],
  "host_permissions": [
    "https://chat.openai.com/*",
    "https://claude.ai/*",
    "https://gemini.google.com/*",
    "https://grok.x.ai/*",
    "http://localhost:8000/*"
  ],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": [
        "https://chat.openai.com/*",
        "https://claude.ai/*",
        "https://gemini.google.com/*",
        "https://grok.x.ai/*"
      ],
      "js": ["content.js"],
      "css": ["styles.css"]
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "web_accessible_resources": [
    {
      "resources": ["icons/*", "fonts/*"],
      "matches": ["<all_urls>"]
    }
  ]
}
EOF

# Create README
cd ..
cat > README.md << 'EOF'
# Martin - AI Prompt Optimizer

Martin is a Chrome extension that provides real-time prompt optimization for developers using Grok 3 AI.

## Quick Start

1. **Backend Setup**
   ```bash
   cd backend
   cp .env.example .env
   # Add your GROK3_API_KEY to .env
   docker-compose up -d
   # Or: python martin_backend.py
   ```

2. **Extension Setup**
   ```bash
   cd extension
   npm install
   npm run build
   ```

3. **Install in Chrome**
   - Open chrome://extensions/
   - Enable Developer mode
   - Load unpacked → select dist folder

## Features

- Real-time prompt analysis
- Model-specific optimizations
- Token usage reduction
- Developer-focused suggestions

## License

MIT
EOF

echo "✅ Martin setup complete!"
echo ""
echo "Next steps:"
echo "1. cd backend"
echo "2. cp .env.example .env"
echo "3. Edit .env and add your GROK3_API_KEY"
echo "4. Copy the martin_backend.py code from the previous response"
echo "5. docker-compose up -d (or python martin_backend.py)"
echo "6. cd ../extension && npm install && npm run build"
echo "7. Load the extension in Chrome"