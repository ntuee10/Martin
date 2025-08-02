# Martin - AI Prompt Optimizer

Martin is a Chrome extension that provides real-time prompt optimization for developers using advanced AI (Grok 3).

## Features

- 🚀 Real-time prompt analysis with <200ms latency
- 🎯 Model-specific optimizations (GPT-4, Claude, Gemini, Grok)
- 💡 Developer-focused suggestions with code examples
- ⚡ Token optimization to reduce costs
- 📊 Analytics dashboard for tracking improvements
- 🔒 Privacy-first with direct Grok 3 API integration

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- Redis (or Docker)
- Grok 3 API key from X.AI

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/ntuee10/martin.git
cd martin/backend
```

2. **Set up environment**
```bash
# Copy environment variables
cp .env.example .env

# Edit .env and add your Grok 3 API key
# GROK3_API_KEY=your_actual_key_here
```

3. **Option A: Run with Docker (Recommended)**
```bash
docker-compose up -d
```

4. **Option B: Run locally**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (in another terminal)
redis-server

# Run the API
python martin_backend.py
```

The API will be available at http://localhost:8000

### Extension Setup

1. **Install dependencies**
```bash
cd ../extension
npm install
```

2. **Build the extension**
```bash
npm run build
```

3. **Install in Chrome**
- Open Chrome and navigate to `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" and select the `dist` folder

### Verify Installation

1. Visit http://localhost:8000/api/v1/health to check the backend
2. The Martin icon should appear in your Chrome toolbar
3. Navigate to ChatGPT, Claude, or Gemini to see Martin in action

## Development

### Running in development mode

**Backend:**
```bash
cd backend
python martin_backend.py  # Auto-reloads on changes
```

**Extension:**
```bash
cd extension
npm run dev  # Watches for changes
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Extension tests
cd extension
npm test
```

## Configuration

### Grok 3 API Setup

1. Get your API key from [X.AI Platform](https://x.ai/api)
2. Add to `.env` file:
```env
GROK3_API_KEY=your_key_here
GROK3_API_URL=https://api.x.ai/v1  # Optional, defaults to X.AI
```

### Extension Settings

Access through the extension popup:
- Suggestion Level: Conservative/Moderate/Aggressive
- Target Models: Select which LLMs to optimize for
- API endpoint: Default is http://localhost:8000

## API Documentation

### Analyze Prompt

```http
POST /api/v1/analyze
Authorization: Bearer {token}
Content-Type: application/json

{
  "prompt": "Write a function that...",
  "target_model": "gpt-4",
  "context": {
    "domain": "technical",
    "session_id": "uuid"
  },
  "options": {
    "suggestion_level": "moderate",
    "optimize_for_tokens": true
  }
}
```

## Deployment

For production deployment:

1. Update `.env` with production settings
2. Use a proper JWT secret key
3. Configure CORS origins for your extension ID
4. Set up SSL/TLS for the API
5. Use a managed Redis instance

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/ntuee10/martin/issues
- Documentation: https://github.com/ntuee10/martin/wiki
