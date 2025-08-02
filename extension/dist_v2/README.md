# Martin v2.0 - Professional Chrome Extension

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
python martin_grok3_v2.py
```

### 2. Load the Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `extension/dist_v2` folder

### 3. Use Martin
- Navigate to ChatGPT, Claude, or any supported AI platform
- Start typing a prompt
- Watch Martin analyze and suggest improvements in real-time!

## ✨ Features

### Grammarly-Style UI
- **Floating Button**: Shows suggestion count with color-coded states
- **Suggestion Cards**: Detailed explanations for each optimization
- **Modal View**: Side-by-side comparison of original vs optimized
- **Real-time Analysis**: Instant feedback as you type

### Developer-Focused Optimizations
- Removes unnecessary politeness ("please", "could you")
- Adds technical specifications (types, error handling)
- Structures prompts for maximum clarity
- Shows token savings and cost reduction

## 🎨 UI States

- **Blue Button**: Ready to analyze
- **Pulsing**: Currently analyzing
- **Orange + Badge**: Has suggestions (count shown)
- **Green**: Prompt optimized

## 📊 Metrics Dashboard

View your optimization impact:
- Clarity Score
- Specificity Score
- Tokens Saved
- Estimated Cost Savings

## 🔧 Configuration

### Backend Settings (.env)
```
GROK3_API_KEY=your_key_here
API_PORT=8000
```

### Extension Settings
Access via the extension popup:
- Enable/Disable Martin
- Toggle inline highlights
- Auto-analyze on typing

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file

---

**Martin v2.0** - Transforming developer prompts into precision instruments.
