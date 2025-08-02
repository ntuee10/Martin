# Martin Developer Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Development](#backend-development)
3. [Extension Development](#extension-development)
4. [API Reference](#api-reference)
5. [Testing Guide](#testing-guide)
6. [Deployment](#deployment)
7. [Contributing](#contributing)

## Architecture Overview

Martin consists of two main components:

```
Martin/
├── backend/                 # Python FastAPI server
│   ├── martin_grok3_v2.py  # Main API server
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
└── extension/              # Chrome Extension
    └── dist_v2/           # Production build
        ├── content.js     # Main content script
        ├── popup.html     # Extension popup
        └── manifest.json  # Extension config
```

### Technology Stack

**Backend:**
- Python 3.8+
- FastAPI for REST API
- Grok3 API for AI analysis
- httpx for async HTTP
- Pydantic for data validation

**Extension:**
- Vanilla JavaScript (ES6+)
- Chrome Extension Manifest V3
- Fetch API for backend communication

## Backend Development

### Setting Up Development Environment

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GROK3_API_KEY
```

4. **Run development server:**
```bash
python martin_grok3_v2.py
# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Backend Architecture

```python
# Core Components

class Grok3Analyzer:
    """Handles prompt analysis using Grok3 API"""
    - analyze_prompt()      # Main analysis method
    - _build_analysis_prompt()  # Constructs Grok3 prompt
    - _generate_analysis()      # Processes results
    - _demo_analysis()          # Fallback for demo mode

# API Endpoints
POST /api/v2/analyze       # Analyze a prompt
GET  /api/v2/health       # Health check
GET  /                    # API info

# Data Models (Pydantic)
- AnalyzeRequest         # Input prompt data
- AnalyzeResponse        # Optimization results
- Suggestion             # Individual suggestion
- PromptMetrics         # Quality metrics
```

### Adding New Optimizations

1. **Update system prompt in `Grok3Analyzer`:**
```python
SYSTEM_PROMPT = """..."""  # Add new optimization rules
```

2. **Add new suggestion types:**
```python
class SuggestionType(str, Enum):
    # ...existing types...
    NEW_TYPE = "new_type"
```

3. **Implement detection logic:**
```python
def _generate_analysis(self, original, optimized, target_model):
    # Add detection for new patterns
    if "pattern" in original:
        suggestions.append(Suggestion(...))
```

### Backend Testing

Run tests with pytest:
```bash
cd backend
pytest -v tests/
```

Write new tests in `tests/test_api.py`:
```python
def test_new_optimization():
    response = client.post("/api/v2/analyze", json={...})
    assert response.status_code == 200
    # Add assertions
```

## Extension Development

### Development Setup

1. **Load unpacked extension:**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `extension/dist_v2/`

2. **Live reload during development:**
   - Make changes to files
   - Click "Reload" in Chrome extensions page
   - Refresh the target website

### Extension Architecture

```javascript
// Core Components

// content.js - Main content script
- createMartinUI()        // Creates UI elements
- detectPlatform()        // Detects AI platform
- analyzePrompt()         // Calls backend API
- showSuggestions()       // Displays suggestions
- findAndMonitorTextarea() // Monitors input

// popup.js - Extension popup
- Settings management
- Statistics display
- API connection status

// background.js - Service worker
- Message handling
- Storage management
- Statistics tracking
```

### Adding Platform Support

1. **Update platform detection:**
```javascript
function detectPlatform() {
  const platforms = {
    'chat.openai.com': 'gpt-4',
    'newplatform.com': 'new-model',  // Add new platform
    // ...
  };
}
```

2. **Add textarea selector:**
```javascript
function findAndMonitorTextarea() {
  const selectors = [
    // ...existing selectors...
    'textarea[data-platform="new"]',  // Add new selector
  ];
}
```

### Styling and UI

Martin uses inline styles for maximum compatibility:

```javascript
// Button states
.martin-button             // Default state
.martin-button.analyzing   // During analysis
.martin-button.has-suggestions  // Has suggestions
.martin-button.optimized   // After optimization

// Colors
#3B82F6  // Primary blue
#F59E0B  // Warning orange
#10B981  // Success green
#EF4444  // Error red
```

## API Reference

### POST /api/v2/analyze

Analyzes a prompt and returns optimization suggestions.

**Request:**
```json
{
  "prompt": "string",
  "target_model": "gpt-4|claude-3|cursor|gemini",
  "context": {
    "domain": "code_generation|debugging|architecture",
    "language": "optional string",
    "framework": "optional string"
  },
  "options": {
    "aggressive_optimization": true,
    "max_suggestions": 5
  }
}
```

**Response:**
```json
{
  "optimized_prompt": "string",
  "suggestions": [
    {
      "type": "clarity|specificity|token_optimization",
      "original": "string",
      "suggested": "string",
      "explanation": "string",
      "confidence": 0.95,
      "token_delta": -10,
      "position": [0, 20]
    }
  ],
  "metrics": {
    "clarity_score": 85.0,
    "specificity_score": 90.0,
    "token_efficiency": 75.0,
    "technical_accuracy": 95.0,
    "overall_quality": 86.25,
    "token_count": 45,
    "token_reduction": 15,
    "estimated_cost_savings": 0.0023
  },
  "processing_time_ms": 234,
  "developer_tips": ["tip1", "tip2"]
}
```

### GET /api/v2/health

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "2.0.0",
  "grok3_connected": true,
  "mode": "production",
  "focus": "developer-optimized"
}
```

## Testing Guide

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_api.py::TestAPI::test_analyze_endpoint_basic

# Run with verbose output
pytest -v
```

### Extension Testing

1. **Manual testing checklist:**
   - [ ] Extension loads on all supported platforms
   - [ ] Martin button appears when typing
   - [ ] Suggestions display correctly
   - [ ] Accept/reject suggestions works
   - [ ] Modal shows optimized prompt
   - [ ] Copy to clipboard functions
   - [ ] Settings persist after reload

2. **Console debugging:**
```javascript
// Enable debug logging
console.log('Martin:', variable);

// Check API calls
console.log('API Request:', requestData);
console.log('API Response:', responseData);
```

## Deployment

### Backend Deployment

1. **Using Docker:**
```bash
cd backend
docker build -t martin-backend .
docker run -p 8000:8000 --env-file .env martin-backend
```

2. **Using systemd (Linux):**
```bash
# Create service file: /etc/systemd/system/martin.service
[Unit]
Description=Martin Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/martin/backend
Environment="PATH=/opt/martin/backend/venv/bin"
ExecStart=/opt/martin/backend/venv/bin/python martin_grok3_v2.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **Environment variables for production:**
```bash
GROK3_API_KEY=your_production_key
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
CORS_ORIGINS=["chrome-extension://your-extension-id"]
```

### Extension Deployment

1. **Build for production:**
```bash
cd extension/dist_v2
zip -r martin-v2.0.0.zip . -x "*.DS_Store" -x "__MACOSX/*"
```

2. **Chrome Web Store submission:**
   - Create developer account
   - Prepare screenshots (1280x800 or 640x400)
   - Write description (132 chars max)
   - Submit for review

3. **Version management:**
   - Update version in `manifest.json`
   - Tag release in Git
   - Create GitHub release

## Contributing

### Code Style

**Python (Backend):**
```bash
# Format with black
black .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .
```

**JavaScript (Extension):**
```javascript
// Use ES6+ features
const functionName = async () => {
  // Prefer arrow functions
};

// Consistent naming
const CONSTANTS_IN_CAPS = true;
const camelCaseVariables = true;
const PascalCaseClasses = true;
```

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Update documentation if needed
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request with description

### Commit Convention

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build process/auxiliary tools

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No sensitive data exposed
- [ ] Performance impact considered
- [ ] Backwards compatibility maintained

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check .env file exists and has valid API key
- Ensure port 8000 is not in use

**Extension not working:**
- Check console for errors (F12)
- Verify backend is running
- Check CORS settings
- Try reloading extension

**API returns demo results:**
- Verify GROK3_API_KEY is set correctly
- Check API key has sufficient credits
- Ensure network connectivity

### Debug Mode

Enable debug logging:
```python
# Backend
LOG_LEVEL=DEBUG python martin_grok3_v2.py
```

```javascript
// Extension
localStorage.setItem('martin_debug', 'true');
```

## Support

- GitHub Issues: https://github.com/ntuee10/Martin/issues
- Documentation: This file
- API Docs: http://localhost:8000/docs (when running)

---

Happy coding with Martin! 🚀
