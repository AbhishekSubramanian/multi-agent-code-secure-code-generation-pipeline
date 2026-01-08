"""
Flask API Server for Multi-Agent Code Generation System
Provides REST API endpoints for the React frontend.
"""

import sys
import os
# Add parent directory to path if running from backend directory
if os.path.basename(os.getcwd()) == 'backend':
    sys.path.insert(0, os.path.dirname(os.getcwd()))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Now import from backend package
from backend.orchestrator import Orchestrator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize orchestrator (will be created per request to allow config changes)
def get_orchestrator(enable_review=True):
    """Create orchestrator instance"""
    return Orchestrator(enable_code_review=enable_review, verbose=False)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "provider": os.environ.get("LLM_PROVIDER", "ollama"),
        "model": os.environ.get("OLLAMA_MODEL") if os.environ.get("LLM_PROVIDER") == "ollama" else os.environ.get("CLAUDE_MODEL")
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    return jsonify({
        "provider": provider,
        "model": os.environ.get("OLLAMA_MODEL") if provider == "ollama" else os.environ.get("CLAUDE_MODEL"),
        "ollama_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    })


@app.route('/api/generate', methods=['POST'])
def generate_code():
    """
    Generate code based on user request

    Request body:
    {
        "request": "Create a function to...",
        "enable_review": true
    }
    """
    try:
        data = request.json
        user_request = data.get('request', '')
        enable_review = data.get('enable_review', True)

        if not user_request:
            return jsonify({
                "status": "error",
                "error": "Request text is required"
            }), 400

        logger.info(f"Generating code for request: {user_request[:50]}...")

        # Create orchestrator and generate code
        orchestrator = get_orchestrator(enable_review=enable_review)
        result = orchestrator.generate_code(user_request)

        logger.info(f"Generation completed with status: {result['status']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error during code generation: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example requests"""
    examples = [
        {
            "id": 1,
            "title": "Fibonacci Calculator",
            "request": "Create a function that calculates fibonacci numbers using recursion with memoization for performance"
        },
        {
            "id": 2,
            "title": "JSON File Reader",
            "request": "Create a function to read a JSON file and return its contents as a dictionary with error handling"
        },
        {
            "id": 3,
            "title": "Email Validator",
            "request": "Create a function that validates email addresses using regex and returns True/False"
        },
        {
            "id": 4,
            "title": "CSV Parser",
            "request": "Write a function to parse CSV files and convert them to a list of dictionaries"
        },
        {
            "id": 5,
            "title": "Password Generator",
            "request": "Create a secure password generator function with configurable length and character types"
        }
    ]
    return jsonify(examples)


@app.route('/api/test-agents', methods=['GET'])
def test_agents():
    """Test individual agents"""
    from backend.agents.syntax_checker.agent import SyntaxCheckerAgent
    from backend.agents.hallucination_detector.agent import HallucinationDetectorAgent

    results = {
        "syntax_checker": {"status": "unknown"},
        "hallucination_detector": {"status": "unknown"}
    }

    try:
        # Test Syntax Checker
        syntax_agent = SyntaxCheckerAgent()
        test_code = "def add(a, b):\n    return a + b"
        syntax_result = syntax_agent.validate(test_code)
        results["syntax_checker"] = {
            "status": "working" if syntax_result["status"] == "SYNTAX_VALID" else "error"
        }

        # Test Hallucination Detector
        hall_agent = HallucinationDetectorAgent()
        test_imports = "import os\nimport json"
        hall_result = hall_agent.verify(test_imports)
        results["hallucination_detector"] = {
            "status": "working" if hall_result["status"] == "VERIFIED" else "error"
        }

    except Exception as e:
        logger.error(f"Error testing agents: {str(e)}")

    return jsonify(results)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting API server on port {port}")
    logger.info(f"LLM Provider: {os.environ.get('LLM_PROVIDER', 'ollama')}")
    app.run(debug=True, port=port, host='0.0.0.0')
