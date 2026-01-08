"""
Syntax Checker Agent
Validates Python code for syntactic correctness.
"""

import ast
import sys
from typing import Dict, Any, List, Optional
from io import StringIO
import re


class SyntaxCheckerAgent:
    """
    Python Syntax Verification Agent that analyzes code for syntax errors.
    """

    def __init__(self):
        """Initialize the Syntax Checker Agent."""
        pass

    def validate(self, code: str, context: str = "") -> Dict[str, Any]:
        """
        Validate Python code for syntax errors.

        Args:
            code: Python code to validate
            context: Optional context about the code

        Returns:
            Dictionary with validation status and error details
        """
        if not code or not code.strip():
            return {
                "status": "PARSE_FAILED",
                "errors": [{
                    "line": 0,
                    "issue": "Empty or whitespace-only code provided",
                    "code": "",
                    "fix": "Provide valid Python code"
                }]
            }

        try:
            # Attempt to parse the code with AST
            ast.parse(code)

            # If successful, code is syntactically correct
            line_count = len(code.split("\n"))

            return {
                "status": "SYNTAX_VALID",
                "message": "The provided Python code is syntactically correct.",
                "summary": {
                    "total_lines": line_count,
                    "syntax_errors": 0,
                    "ready_for_execution": True
                }
            }

        except SyntaxError as e:
            # Syntax error found
            errors = self._parse_syntax_error(e, code)
            corrected_code = self._attempt_correction(code, errors)

            return {
                "status": "SYNTAX_ERROR",
                "message": "The provided Python code contains syntax errors.",
                "errors": errors,
                "corrected_code": corrected_code
            }

        except Exception as e:
            # Other parsing errors
            return {
                "status": "PARSE_FAILED",
                "message": f"Failed to parse code: {str(e)}",
                "errors": [{
                    "line": 0,
                    "issue": str(e),
                    "code": "",
                    "fix": "Review code structure"
                }]
            }

    def _parse_syntax_error(self, error: SyntaxError, code: str) -> List[Dict[str, Any]]:
        """Parse SyntaxError into structured error information"""
        errors = []

        error_info = {
            "line": error.lineno or 0,
            "offset": error.offset or 0,
            "issue": error.msg or "Syntax error",
            "code": (error.text or "").strip() if error.text else "",
            "fix": self._suggest_fix(error, code)
        }

        errors.append(error_info)

        return errors

    def _suggest_fix(self, error: SyntaxError, code: str) -> str:
        """Suggest a fix based on the syntax error"""
        msg = error.msg.lower() if error.msg else ""

        # Common syntax error patterns
        if "invalid syntax" in msg:
            if error.text:
                text = error.text.strip()

                # Missing colon
                if text.startswith(("def ", "class ", "if ", "elif ", "else", "for ", "while ", "try", "except", "finally", "with ")):
                    return f"Add ':' at the end → {text.rstrip()}:"

                # Unclosed parenthesis/bracket/brace
                if "(" in text and ")" not in text:
                    return "Add closing parenthesis ')'"
                if "[" in text and "]" not in text:
                    return "Add closing bracket ']'"
                if "{" in text and "}" not in text:
                    return "Add closing brace '}'"

                # Unclosed string
                if text.count('"') % 2 != 0:
                    return 'Add closing double quote "'
                if text.count("'") % 2 != 0:
                    return "Add closing single quote '"

            return "Check syntax around this line"

        elif "unexpected eof" in msg or "eof while parsing" in msg:
            return "Check for unclosed brackets, parentheses, or quotes"

        elif "unterminated string" in msg:
            return "Add closing quote to string literal"

        elif "invalid character" in msg:
            return "Remove or replace invalid character"

        elif "cannot assign to" in msg:
            return "Left side of assignment must be a variable"

        elif "positional argument follows keyword argument" in msg:
            return "Move positional arguments before keyword arguments"

        else:
            return "Review Python syntax for this line"

    def _attempt_correction(self, code: str, errors: List[Dict[str, Any]]) -> Optional[str]:
        """
        Attempt automatic correction of simple syntax errors.

        Returns corrected code or None if unable to correct.
        """
        if not errors:
            return None

        lines = code.split("\n")
        modified = False

        for error in errors:
            line_num = error["line"] - 1  # Convert to 0-indexed

            if line_num < 0 or line_num >= len(lines):
                continue

            line = lines[line_num]

            # Try simple fixes
            # Fix 1: Missing colon
            if "Add ':' at the end" in error["fix"]:
                if not line.rstrip().endswith(":"):
                    lines[line_num] = line.rstrip() + ":"
                    modified = True

            # Fix 2: Unclosed parenthesis (simple case)
            elif "Add closing parenthesis ')'" in error["fix"]:
                if line.count("(") > line.count(")"):
                    lines[line_num] = line.rstrip() + ")"
                    modified = True

            # Fix 3: Unclosed bracket
            elif "Add closing bracket ']'" in error["fix"]:
                if line.count("[") > line.count("]"):
                    lines[line_num] = line.rstrip() + "]"
                    modified = True

        if modified:
            corrected = "\n".join(lines)
            # Verify the correction is valid
            try:
                ast.parse(corrected)
                return corrected
            except:
                return None

        return None

    def check_multiple(self, code_snippets: List[str]) -> Dict[str, Any]:
        """
        Validate multiple code snippets.

        Args:
            code_snippets: List of Python code strings

        Returns:
            Dictionary with overall validation status
        """
        results = []
        all_valid = True

        for i, code in enumerate(code_snippets):
            result = self.validate(code, context=f"Snippet {i+1}")
            results.append(result)

            if result["status"] != "SYNTAX_VALID":
                all_valid = False

        return {
            "overall_status": "ALL_VALID" if all_valid else "ERRORS_FOUND",
            "total_snippets": len(code_snippets),
            "valid_snippets": sum(1 for r in results if r["status"] == "SYNTAX_VALID"),
            "results": results
        }


if __name__ == "__main__":
    # Example usage
    agent = SyntaxCheckerAgent()

    # Test valid code
    valid_code = """
def greet(name: str) -> str:
    message = f"Hello, {name}!"
    return message
"""

    result = agent.validate(valid_code)
    print("Valid Code Test:")
    print(f"Status: {result['status']}")
    print()

    # Test invalid code
    invalid_code = """
def greet(name)
    message = f"Hello, {name}!"
    print(message
"""

    result = agent.validate(invalid_code)
    print("Invalid Code Test:")
    print(f"Status: {result['status']}")
    if "errors" in result:
        print("Errors found:")
        for error in result["errors"]:
            print(f"  Line {error['line']}: {error['issue']}")
            print(f"  Fix: {error['fix']}")

    if result.get("corrected_code"):
        print("\nAuto-corrected code:")
        print(result["corrected_code"])
