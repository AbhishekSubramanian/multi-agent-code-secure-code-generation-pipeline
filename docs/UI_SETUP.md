# Web UI Setup Guide

A beautiful React-based web interface for the Multi-Agent Code Generation System.

## Features

- 🎨 Clean, modern UI with intuitive design
- 🚀 Real-time code generation with progress indicators
- 📋 One-click code copying
- 💡 Pre-built example requests
- ✅ Visual pipeline status tracking
- 📊 Code review display
- 🔄 Support for both Claude and Ollama
- 📱 Responsive design

---

## Quick Start

### Prerequisites

1. **Python Backend Setup**
   - Completed Python environment setup
   - Dependencies installed (`pip install -r requirements.txt`)
   - `.env` file configured with your LLM provider

2. **Node.js & npm**
   - Node.js 14 or higher
   - Download from: https://nodejs.org/

### Step 1: Install Backend Dependencies

```bash
# Install Flask and CORS support
pip install flask flask-cors
```

Or simply:

```bash
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install
```

This will install:
- React
- React DOM
- Axios (for API calls)
- React Scripts (build tools)

### Step 3: Start the Backend API Server

Open a **new terminal** and run:

```bash
# From the project root directory
python api_server.py
```

You should see:
```
Starting API server on port 5000
LLM Provider: ollama (or claude)
* Running on http://0.0.0.0:5000
```

**Keep this terminal running!**

### Step 4: Start the Frontend Development Server

Open **another terminal** and run:

```bash
# From the frontend directory
cd frontend
npm start
```

The React app will automatically open in your browser at:
```
http://localhost:3000
```

---

## Usage

### 1. Enter Your Request

In the left panel, type your code generation request:
```
Create a function to validate email addresses using regex
```

### 2. Configure Options

- ✅ **Enable Code Review**: Toggle to include/exclude code review step
- The current LLM provider and model are shown in the header

### 3. Generate Code

Click **"⚡ Generate Code"** button

Watch the progress indicator as the system:
1. Generates code
2. Validates syntax
3. Checks for hallucinations
4. Reviews code quality (if enabled)

### 4. View Results

The right panel displays:
- ✅ **Generated Code**: Ready to copy and use
- 📋 **Copy Button**: One-click clipboard copy
- 🔄 **Pipeline Status**: Visual confirmation of each step
- 📊 **Code Review**: Quality analysis (if enabled)
- 📝 **Metadata**: Request ID and attempt count

### 5. Try Examples

Click any example in the "Example Requests" section to auto-fill the input.

---

## API Endpoints

The backend provides these REST API endpoints:

### `GET /api/health`
Health check and configuration info
```json
{
  "status": "healthy",
  "provider": "ollama",
  "model": "deepseek-coder:6.7b"
}
```

### `GET /api/config`
Get current LLM configuration
```json
{
  "provider": "ollama",
  "model": "deepseek-coder:6.7b",
  "ollama_url": "http://localhost:11434/v1"
}
```

### `POST /api/generate`
Generate code
```json
{
  "request": "Create a function...",
  "enable_review": true
}
```

### `GET /api/examples`
Get example requests
```json
[
  {
    "id": 1,
    "title": "Fibonacci Calculator",
    "request": "Create a function..."
  }
]
```

---

## Project Structure

```
agents-lanchain/
├── api_server.py              # Flask backend API
├── orchestrator.py            # Multi-agent orchestrator
├── agents/                    # Agent implementations
├── frontend/                  # React UI
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   └── index.js          # React entry point
│   ├── package.json          # npm dependencies
│   └── .gitignore
├── requirements.txt          # Python dependencies
├── .env                      # Configuration
└── UI_SETUP.md              # This file
```

---

## Troubleshooting

### Issue: "Cannot connect to backend" / Network errors

**Solution 1:** Make sure the backend is running
```bash
python api_server.py
```

**Solution 2:** Check if port 5000 is available
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

**Solution 3:** Try a different port
Edit `api_server.py`:
```python
port = int(os.environ.get('PORT', 5001))  # Change to 5001
```

Then update `frontend/package.json`:
```json
"proxy": "http://localhost:5001"
```

### Issue: Frontend won't start / npm errors

**Solution:** Clear cache and reinstall
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Issue: "Module not found" errors

**Solution:** Install missing dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: Code generation fails

**Check:**
1. Is Ollama running? (if using Ollama)
   ```bash
   ollama list
   ```

2. Is your API key valid? (if using Claude)
   - Check `.env` file
   - Verify `ANTHROPIC_API_KEY`

3. Check backend logs in the terminal running `api_server.py`

### Issue: Slow generation

**Causes:**
- Large model (if using Ollama)
- Limited RAM/CPU
- Network latency (if using Claude)

**Solutions:**
- Use a smaller model (e.g., `deepseek-coder:1.3b`)
- Disable code review for faster results
- Close other applications

---

## Customization

### Change Port Numbers

**Backend (default: 5000):**
Edit `api_server.py`:
```python
port = int(os.environ.get('PORT', 8080))
```

**Frontend (default: 3000):**
Create `frontend/.env`:
```
PORT=8080
```

### Add More Examples

Edit `api_server.py`, find the `get_examples()` function:
```python
examples = [
    {
        "id": 6,
        "title": "Your Example",
        "request": "Your request text..."
    }
]
```

### Modify UI Colors

Edit `frontend/src/App.css`:
```css
:root {
  --primary-color: #6366f1;  /* Change to your color */
  --primary-dark: #4f46e5;
}
```

### Change Default Settings

Edit `frontend/src/App.js`:
```javascript
const [enableReview, setEnableReview] = useState(false); // Disable by default
```

---

## Building for Production

### Build the Frontend

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/build/`.

### Serve Static Files with Flask

Modify `api_server.py` to serve the built React app:

```python
from flask import send_from_directory
import os

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend/build', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(f'frontend/build/{path}'):
        return send_from_directory('frontend/build', path)
    return send_from_directory('frontend/build', 'index.html')
```

Then run:
```bash
python api_server.py
```

Access the app at: `http://localhost:5000`

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Frontend**: Auto-reloads when you edit React files
- **Backend**: Auto-reloads when you edit Python files (Flask debug mode)

### Debug Mode

**Backend:**
Already enabled in `api_server.py`:
```python
app.run(debug=True, port=5000)
```

**Frontend:**
React DevTools: Install browser extension for React debugging

### API Testing

Use the browser console or tools like Postman to test API endpoints:

```javascript
// In browser console
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
```

---

## Security Notes

**For Production:**

1. **Disable CORS for specific origins:**
   ```python
   CORS(app, origins=["https://yourdomain.com"])
   ```

2. **Disable Flask debug mode:**
   ```python
   app.run(debug=False)
   ```

3. **Use environment variables for sensitive data:**
   - Never commit `.env` to git
   - Use `.env.example` as template

4. **Add rate limiting:**
   ```bash
   pip install flask-limiter
   ```

---

## Next Steps

1. ✅ Start backend: `python api_server.py`
2. ✅ Start frontend: `cd frontend && npm start`
3. ✅ Open browser: `http://localhost:3000`
4. ✅ Generate your first code!

For questions or issues, refer to the main `README.md` or `OLLAMA_SETUP.md`.

---

## Screenshots Guide

### Main Interface
- **Left Panel**: Code request input and examples
- **Right Panel**: Generated code and results
- **Header**: Current provider and model info

### Status Indicators
- 🟢 Green: Success
- 🔵 Blue: In Progress
- 🔴 Red: Error/Failed

### Example Workflow
1. Click "Fibonacci Calculator" example
2. Request auto-fills
3. Click "Generate Code"
4. Watch pipeline progress
5. Copy generated code
6. View code review

---

Enjoy your new UI! 🎉
