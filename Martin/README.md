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
