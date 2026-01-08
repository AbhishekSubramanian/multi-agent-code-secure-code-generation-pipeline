# Multi-Agent Code Generation System

A Claude Code-based multi-agent system for generating, validating, and reviewing Python code.

## 🏗️ Architecture

### Project Structure

```
agents-lanchain/
├── backend/                           # Backend Python code
│   ├── __init__.py
│   ├── orchestrator.py                # Main orchestrator implementation
│   ├── api_server.py                  # Flask API server for HTTP endpoints
│   ├── requirements.txt               # Python dependencies
│   │
│   └── agents/                        # Agent modules
│       ├── __init__.py
│       │
│       ├── orchestrator/
│       │   └── CLAUDE.md              # Orchestrator agent specification
│       │
│       ├── code_generator/
│       │   ├── __init__.py
│       │   ├── agent.py               # Code Generator implementation
│       │   └── CLAUDE.md              # Agent specification
│       │
│       ├── syntax_checker/
│       │   ├── __init__.py
│       │   ├── agent.py               # Syntax Checker implementation
│       │   └── CLAUDE.md              # Agent specification
│       │
│       ├── hallucination_detector/
│       │   ├── __init__.py
│       │   ├── agent.py               # Hallucination Detector implementation
│       │   └── CLAUDE.md              # Agent specification
│       │
│       └── code_reviewer/
│           ├── __init__.py
│           ├── agent.py               # Code Reviewer implementation
│           └── CLAUDE.md              # Agent specification
│
├── frontend/                          # React web interface
│   ├── src/                           # React source files
│   ├── public/                        # Static assets
│   ├── package.json                   # Node.js dependencies
│   └── README.md                      # Frontend documentation
│
├── scripts/                           # Utility scripts
│   ├── example.py                     # Example usage demonstrations
│   ├── start-ui.sh                    # Linux/Mac UI startup script
│   └── start-ui.bat                   # Windows UI startup script
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_system.py                 # System integration tests
│   └── README.md                      # Testing documentation
│
├── examples/                          # Example generated code
│   ├── __init__.py
│   ├── add.py                         # Simple addition example
│   ├── calculator.py                  # Comprehensive calculator example
│   └── README.md                      # Examples documentation
│
├── docs/                              # Documentation
│   ├── OLLAMA_SETUP.md                # Ollama integration guide
│   └── UI_SETUP.md                    # Frontend setup instructions
│
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore patterns
└── README.md                          # This file
```

## 🤖 Agents

### 1. Code Generator Agent
**Purpose**: Generates Python code based on user requirements.

**Key Features**:
- Python-only code generation
- PEP 8 compliant output
- Includes docstrings and type hints
- Error handling built-in

**Location**: `backend/agents/code_generator/CLAUDE.md`

---

### 2. Syntax Checker Agent
**Purpose**: Validates that generated code is syntactically correct.

**Key Features**:
- Identifies all syntax errors
- Provides precise line numbers
- Suggests fixes for errors
- Returns corrected code

**Location**: `backend/agents/syntax_checker/CLAUDE.md`

---

### 3. Hallucination Detector Agent
**Purpose**: Ensures all referenced libraries, functions, and APIs actually exist.

**Key Features**:
- Verifies import statements
- Checks function signatures
- Validates method calls
- Provides alternatives for hallucinated components

**Location**: `backend/agents/hallucination_detector/CLAUDE.md`

---

### 4. Code Reviewer Agent (Generic)
**Purpose**: Provides comprehensive code review for any programming language.

**Key Features**:
- Correctness & logic analysis
- Security vulnerability detection
- Performance evaluation
- Maintainability assessment
- Actionable recommendations

**Location**: `backend/agents/code_reviewer/CLAUDE.md`

---

### 5. Orchestrator Agent
**Purpose**: Coordinates the workflow between all agents.

**Key Features**:
- Manages agent pipeline
- Handles retries on failures
- Aggregates results
- Ensures quality gates

**Location**: `backend/agents/orchestrator/CLAUDE.md`

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and add your Anthropic API key
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### Running the System

#### Option 1: Web UI (Recommended)
Run the full-stack application with React frontend:

**Linux/Mac:**
```bash
bash scripts/start-ui.sh
```

**Windows:**
```cmd
scripts\start-ui.bat
```

The UI will be available at `http://localhost:3000` and the backend API at `http://localhost:5000`.

For detailed UI setup instructions, see [docs/UI_SETUP.md](docs/UI_SETUP.md).

#### Option 2: Interactive Examples
```bash
python scripts/example.py
```

Choose from:
1. Run example requests (pre-configured demonstrations)
2. Run single custom request (enter your own request)
3. Test individual agents (unit tests for each agent)

#### Option 3: Programmatic Usage
```python
from backend.orchestrator import Orchestrator

# Initialize the orchestrator
orchestrator = Orchestrator(enable_code_review=True, verbose=True)

# Generate code
request = "Create a function to calculate Fibonacci numbers"
result = orchestrator.generate_code(request)

# Display results
print(orchestrator.format_response(result))
```

#### Option 4: Use Individual Agents

```python
from backend.agents.code_generator import CodeGeneratorAgent
from backend.agents.syntax_checker import SyntaxCheckerAgent

# Use Code Generator alone
generator = CodeGeneratorAgent()
result = generator.generate({
    "action": "generate",
    "request": "Create a hello world function",
    "constraints": ["python_only"]
})

# Use Syntax Checker alone
checker = SyntaxCheckerAgent()
validation = checker.validate(result["code"])
```

### Example Workflow

```
User Request: "Create a function to parse JSON files"
         │
         ▼
┌─────────────────────┐
│   Code Generator    │ → Generates Python function
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Syntax Checker    │ → Validates syntax ✓
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Hallucination Det.  │ → Verifies json module exists ✓
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Code Reviewer     │ → Reviews for best practices
└─────────────────────┘
         │
         ▼
    Final Output
```

## 📋 Agent Communication

Agents communicate using structured formats:

### Status Codes
| Code | Meaning |
|------|---------|
| `SYNTAX_VALID` | Code passed syntax check |
| `SYNTAX_ERROR` | Syntax errors found |
| `VERIFIED` | All references valid |
| `HALLUCINATION_DETECTED` | Found fabricated components |

## 🔧 Customization

### Adding New Agents

1. Create a new folder under `backend/agents/`
2. Add a `CLAUDE.md` file with:
   - Role definition
   - Core directives
   - Output format
   - Behavioral guidelines
   - Inter-agent communication protocol

### Modifying Existing Agents

Edit the relevant `CLAUDE.md` file to:
- Adjust behavioral guidelines
- Modify output formats
- Add new capabilities
- Change validation rules

## 📝 License

MIT License - Feel free to use and modify for your projects.

