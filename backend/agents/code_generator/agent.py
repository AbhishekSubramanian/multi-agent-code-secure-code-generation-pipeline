"""
Code Generator Agent
Generates clean, functional, and well-documented Python code.
Supports both Claude (Anthropic) and Ollama (local models).
"""

import re
from typing import Dict, Any, List
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CodeGeneratorAgent:
    """
    Python Code Generator Agent that creates code based on user requirements.

    Follows PEP 8 guidelines and generates syntactically correct, well-documented code.
    Supports both Claude (Anthropic) and Ollama (local models).
    """

    def __init__(self, model: str = None):
        """
        Initialize the Code Generator Agent.

        Args:
            model: Model to use (auto-detected from env if not specified)
        """
        # Determine LLM provider
        self.provider = os.environ.get("LLM_PROVIDER", "ollama").lower()

        # Initialize client based on provider
        if self.provider == "claude":
            from anthropic import Anthropic
            self.model = model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
            self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            self.client_type = "claude"
        else:  # ollama
            from openai import OpenAI
            self.model = model or os.environ.get("OLLAMA_MODEL", "deepseek-coder:6.7b")
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.client = OpenAI(
                base_url=base_url,
                api_key="ollama"  # Ollama doesn't need a real API key
            )
            self.client_type = "ollama"

        # Load agent instructions from CLAUDE.md
        claude_md_path = Path(__file__).parent / "CLAUDE.md"
        with open(claude_md_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def generate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Python code based on request.

        Args:
            request_data: Dictionary containing:
                - action: "generate"
                - request: User's code request
                - constraints: List of constraints
                - previous_attempt: (optional) Previous code if retry
                - feedback: (optional) Error feedback if retry

        Returns:
            Dictionary with status and generated code
        """
        user_request = request_data.get("request", "")

        # Build the prompt
        prompt = f"Generate Python code for the following request:\n\n{user_request}\n\n"

        # Add feedback if this is a retry
        if "feedback" in request_data and "previous_attempt" in request_data:
            prompt += f"\n\n### Previous Attempt Issues:\n{request_data['feedback']}\n\n"
            prompt += f"### Previous Code:\n```python\n{request_data['previous_attempt']}\n```\n\n"
            prompt += "Please fix the issues and generate corrected code.\n"

        prompt += "\nProvide only the Python code within ```python code blocks. Include all imports, docstrings, type hints, and error handling."

        try:
            # Call LLM API based on client type
            if self.client_type == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text
            else:  # ollama
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4096,
                    temperature=0.7
                )
                content = response.choices[0].message.content

            # Extract code from response
            code = self._extract_code_from_response(content)

            if not code:
                return {
                    "status": "error",
                    "error": "No code block found in response",
                    "raw_response": content
                }

            return {
                "status": "success",
                "code": code,
                "explanation": self._extract_explanation(content),
                "dependencies": self._extract_dependencies(content)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from markdown code blocks"""
        # Look for ```python ... ``` blocks
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            # Return the first code block found
            return matches[0].strip()

        # Fallback: try generic code blocks
        pattern = r"```\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        return ""

    def _extract_explanation(self, response: str) -> str:
        """Extract explanation from response"""
        # Remove code blocks
        text = re.sub(r"```.*?```", "", response, flags=re.DOTALL)

        # Look for explanation section
        if "## Explanation" in text:
            parts = text.split("## Explanation")
            if len(parts) > 1:
                explanation = parts[1].split("##")[0].strip()
                return explanation

        return text.strip()

    def _extract_dependencies(self, response: str) -> List[str]:
        """Extract dependencies from response"""
        dependencies = []

        # Look for Dependencies section
        if "## Dependencies" in response:
            parts = response.split("## Dependencies")
            if len(parts) > 1:
                deps_section = parts[1].split("##")[0].strip()
                # Extract package names from bullet points or lines
                for line in deps_section.split("\n"):
                    line = line.strip().lstrip("-*•").strip()
                    if line and not line.startswith("None") and not line.startswith("No "):
                        dependencies.append(line)

        return dependencies


if __name__ == "__main__":
    # Example usage
    agent = CodeGeneratorAgent()

    request = {
        "action": "generate",
        "request": "Create a function to calculate the factorial of a number",
        "constraints": ["python_only", "no_placeholders"]
    }

    result = agent.generate(request)

    if result["status"] == "success":
        print("Generated Code:")
        print(result["code"])
        print("\nExplanation:")
        print(result["explanation"])
    else:
        print(f"Error: {result['error']}")
