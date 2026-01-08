# Multi-Agent Code Generator - Web UI

A modern React-based web interface for the Multi-Agent Code Generation System.

## Quick Start

### From Project Root

**Windows:**
```bash
start-ui.bat
```

**Linux/Mac:**
```bash
./start-ui.sh
```

### Manual Start

**Terminal 1 - Backend:**
```bash
# From project root
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
# From project root
cd frontend
npm install  # First time only
npm start
```

## Access

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:5000

## Features

- Real-time code generation
- Visual pipeline status
- Code review display
- Example requests
- Copy to clipboard
- Responsive design

## Documentation

See `../UI_SETUP.md` for complete setup and usage instructions.

## Tech Stack

- **Frontend:** React, Axios
- **Backend:** Flask, Flask-CORS
- **Styling:** Custom CSS (no framework)
- **Icons:** Unicode emoji
