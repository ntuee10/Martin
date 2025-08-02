# Martin Quick Reference Card

## 🚀 Quick Start
```bash
# 1. Start Backend
cd backend && python martin_grok3_v2.py

# 2. Load Extension  
Chrome → chrome://extensions/ → Load unpacked → select dist_v2/

# 3. Use Martin
Go to ChatGPT/Claude → Type prompt → Click Martin button
```

## 🎯 Optimization Patterns

### ❌ Avoid → ✅ Use Instead

**Vague Requests:**
❌ "help me create a function"
✅ "Create function validateEmail(email: string): boolean"

**Missing Specs:**
❌ "build an API"  
✅ "REST API: GET /users, POST /users, Auth: JWT"

**No Error Handling:**
❌ "parse JSON data"
✅ "Parse JSON: handle malformed data, return Result<T, Error>"

**Verbose Language:**
❌ "Could you please help me..."
✅ "Create..." / "Fix..." / "Implement..."

## 💡 Pro Tips

1. **Start with action verbs**: Create, Implement, Fix, Debug, Refactor
2. **Specify types**: Always include input/output types
3. **Add constraints**: Performance requirements, error handling
4. **Include examples**: Show expected input/output
5. **Be explicit**: Name files, line numbers, error messages

## 🔧 Common Patterns

### Function Request
```
Create [functionName]:
- Input: [type with schema]
- Process: [specific steps]
- Output: [type with example]
- Handle: [error cases]
```

### Debug Request
```
Debug [error type] in [file:line]:
- Error: [exact message]
- Expected: [behavior]
- Current: [what happens]
- Context: [relevant code]
```

### Component Request
```
Create [Component] component:
- Props: [TypeScript interface]
- State: [state management]
- Features: [list of features]
- Style: [CSS framework]
```

## 📊 Martin UI States

🔵 **Blue** = Ready to analyze
🟡 **Pulsing** = Analyzing prompt
🟠 **Orange + Badge** = Has suggestions
🟢 **Green** = Optimized

## ⌨️ Keyboard Shortcuts

- Click Martin button = Show suggestions
- ESC = Close suggestion card
- Enter = Accept optimization

## 🛠️ Troubleshooting

**Martin button not appearing?**
- Check backend is running
- Reload the extension
- Refresh the webpage

**No suggestions showing?**
- Prompt must be >10 characters
- Check API connection in popup
- Look for console errors (F12)

**API Connection Failed?**
```bash
# Check backend
curl http://localhost:8000/api/v2/health

# Check logs
python martin_grok3_v2.py  # Look for errors
```

## 📝 Example Transformations

**API Design:**
```
Before: "I need user management"
After:  "User CRUD API:
        POST /users {email, password} → {id, token}
        GET /users/:id → User
        Auth: Bearer JWT"
```

**React Component:**
```
Before: "make a form"
After:  "Create ContactForm:
        Fields: name*, email*, message*
        Validation: email regex, min length
        Submit: POST /api/contact
        UI: Tailwind, loading states"
```

---
**Martin v2.0** | Transform prompts → Get better code | https://github.com/ntuee10/Martin
