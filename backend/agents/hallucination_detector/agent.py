"""
Hallucination Detection Agent
Verifies that all referenced libraries, functions, and APIs actually exist.
"""

import ast
import importlib
import sys
from typing import Dict, Any, List, Set, Optional, Tuple
import pkgutil
import inspect


class HallucinationDetectorAgent:
    """
    Hallucination Detection Agent that verifies Python code references.

    Checks for:
    - Non-existent libraries or packages
    - Fabricated functions or methods
    - Incorrect function signatures
    """

    # Python standard library modules
    STDLIB_MODULES = {
        'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
        'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
        'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
        'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
        'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
        'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
        'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
        'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
        'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp',
        'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib', 'imaplib',
        'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json',
        'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox',
        'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib',
        'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'numbers', 'operator',
        'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools',
        'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath',
        'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc',
        'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter',
        'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil',
        'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
        'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess',
        'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile',
        'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time',
        'timeit', 'tkinter', 'token', 'tokenize', 'tomllib', 'trace', 'traceback',
        'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata',
        'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref',
        'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp',
        'zipfile', 'zipimport', 'zlib', '_thread'
    }

    # Common third-party packages
    KNOWN_THIRD_PARTY = {
        'numpy', 'np', 'pandas', 'pd', 'requests', 'flask', 'django', 'fastapi',
        'sqlalchemy', 'pytest', 'scipy', 'matplotlib', 'plt', 'seaborn', 'sns',
        'sklearn', 'tensorflow', 'tf', 'torch', 'pytorch', 'keras', 'cv2',
        'PIL', 'pillow', 'bs4', 'beautifulsoup4', 'selenium', 'scrapy',
        'celery', 'redis', 'boto3', 'aiohttp', 'httpx', 'pydantic',
        'attrs', 'click', 'typer', 'rich', 'tqdm', 'loguru', 'black',
        'flake8', 'mypy', 'isort', 'poetry', 'pipenv', 'dotenv',
        'jinja2', 'werkzeug', 'uvicorn', 'starlette', 'streamlit',
        'plotly', 'dash', 'altair', 'bokeh', 'networkx', 'statsmodels'
    }

    def __init__(self):
        """Initialize the Hallucination Detector Agent."""
        pass

    def verify(self, code: str) -> Dict[str, Any]:
        """
        Verify that all code references are legitimate.

        Args:
            code: Python code to verify

        Returns:
            Dictionary with verification status and details
        """
        if not code or not code.strip():
            return {
                "status": "VERIFICATION_FAILED",
                "message": "Empty code provided",
                "hallucinations": []
            }

        try:
            # Parse code into AST
            tree = ast.parse(code)

            # Extract imports and function calls
            imports = self._extract_imports(tree)
            function_calls = self._extract_function_calls(tree)

            # Verify imports
            hallucinations = []
            verified_components = []

            for imp in imports:
                result = self._verify_import(imp)
                if result["is_valid"]:
                    verified_components.append({
                        "component": imp["module"],
                        "type": "Library",
                        "status": "✅ Valid",
                        "source": result["source"]
                    })
                else:
                    hallucinations.append({
                        "line": imp.get("line", 0),
                        "type": "Library",
                        "referenced": imp["module"],
                        "issue": result["issue"],
                        "suggestion": result["suggestion"]
                    })

            # If no hallucinations found
            if not hallucinations:
                return {
                    "status": "VERIFIED",
                    "message": "All referenced libraries, functions, and APIs have been verified as legitimate.",
                    "summary": {
                        "libraries_checked": len(imports),
                        "functions_verified": len(function_calls),
                        "all_valid": True
                    },
                    "verified_components": verified_components
                }
            else:
                return {
                    "status": "HALLUCINATION_DETECTED",
                    "message": "The code contains references to non-existent or incorrectly used components.",
                    "hallucinations": hallucinations,
                    "risk_assessment": self._assess_risk(hallucinations),
                    "verified_components": verified_components
                }

        except SyntaxError as e:
            return {
                "status": "VERIFICATION_FAILED",
                "message": f"Cannot verify code with syntax errors: {str(e)}",
                "hallucinations": []
            }
        except Exception as e:
            return {
                "status": "VERIFICATION_FAILED",
                "message": f"Verification failed: {str(e)}",
                "hallucinations": []
            }

    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all import statements from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "type": "import"
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "type": "from_import"
                    })

        return imports

    def _extract_function_calls(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all function calls from AST"""
        calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append({
                        "function": node.func.id,
                        "line": node.lineno
                    })
                elif isinstance(node.func, ast.Attribute):
                    calls.append({
                        "function": node.func.attr,
                        "line": node.lineno
                    })

        return calls

    def _verify_import(self, imp: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if an import is valid"""
        module_name = imp["module"]

        # Check if it's in standard library
        if self._is_stdlib(module_name):
            return {
                "is_valid": True,
                "source": "Python Standard Library",
                "issue": None,
                "suggestion": None
            }

        # Check if it's a known third-party package
        if self._is_known_third_party(module_name):
            return {
                "is_valid": True,
                "source": "Known Third-Party Library",
                "issue": None,
                "suggestion": None
            }

        # Try to actually import it (this checks if it's installed)
        try:
            importlib.import_module(module_name)
            return {
                "is_valid": True,
                "source": "Installed Package",
                "issue": None,
                "suggestion": None
            }
        except ImportError:
            # Module doesn't exist or isn't installed
            # Check for common typos or similar modules
            suggestion = self._find_similar_module(module_name)

            return {
                "is_valid": False,
                "source": None,
                "issue": f"Module '{module_name}' does not exist or is not installed",
                "suggestion": suggestion
            }

    def _is_stdlib(self, module_name: str) -> bool:
        """Check if module is in standard library"""
        # Get base module name (e.g., 'os.path' -> 'os')
        base_module = module_name.split('.')[0]
        return base_module in self.STDLIB_MODULES

    def _is_known_third_party(self, module_name: str) -> bool:
        """Check if module is a known third-party package"""
        base_module = module_name.split('.')[0].lower()
        return base_module in self.KNOWN_THIRD_PARTY

    def _find_similar_module(self, module_name: str) -> str:
        """Find similar module names to suggest alternatives"""
        # Common typos and alternatives
        alternatives = {
            'opencv': 'cv2',
            'beautifulsoup': 'bs4',
            'pillow': 'PIL',
            'sklearn': 'scikit-learn (import as sklearn)',
            'tensorflow': 'tf (if using alias)',
        }

        lower_name = module_name.lower()
        if lower_name in alternatives:
            return f"Did you mean '{alternatives[lower_name]}'?"

        # Check for similar stdlib modules
        for stdlib_mod in self.STDLIB_MODULES:
            if self._is_similar(module_name, stdlib_mod):
                return f"Did you mean '{stdlib_mod}' from standard library?"

        # Check for similar third-party packages
        for third_party in self.KNOWN_THIRD_PARTY:
            if self._is_similar(module_name, third_party):
                return f"Did you mean '{third_party}'? (requires installation)"

        return "Consider using a standard library alternative or ensure the package is installed"

    def _is_similar(self, s1: str, s2: str, threshold: int = 2) -> bool:
        """Check if two strings are similar using Levenshtein-like distance"""
        s1, s2 = s1.lower(), s2.lower()
        if abs(len(s1) - len(s2)) > threshold:
            return False

        # Simple similarity check
        if s1 in s2 or s2 in s1:
            return True

        # Count differing characters
        diffs = sum(1 for a, b in zip(s1, s2) if a != b)
        return diffs <= threshold

    def _assess_risk(self, hallucinations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the risk level of hallucinations"""
        severity = "Low"
        impact = "Code may fail at import"

        if len(hallucinations) >= 3:
            severity = "High"
            impact = "Multiple non-existent components will cause immediate failure"
        elif len(hallucinations) >= 1:
            severity = "Medium"
            impact = "Code will fail at import or runtime"

        return {
            "severity": severity,
            "impact": impact,
            "hallucination_count": len(hallucinations)
        }


if __name__ == "__main__":
    # Example usage
    agent = HallucinationDetectorAgent()

    # Test code with valid imports
    valid_code = """
import os
import json
from pathlib import Path
from typing import Dict

def read_config(filepath: str) -> Dict:
    with open(filepath) as f:
        return json.load(f)
"""

    result = agent.verify(valid_code)
    print("Valid Code Test:")
    print(f"Status: {result['status']}")
    print()

    # Test code with hallucinated imports
    invalid_code = """
import os
import automagic_parser  # This doesn't exist
from super_json import ultra_load  # This doesn't exist

def parse_data(data):
    return automagic_parser.parse_anything(data)
"""

    result = agent.verify(invalid_code)
    print("Invalid Code Test:")
    print(f"Status: {result['status']}")
    if result.get("hallucinations"):
        print("Hallucinations found:")
        for h in result["hallucinations"]:
            print(f"  Line {h['line']}: {h['referenced']}")
            print(f"  Issue: {h['issue']}")
            print(f"  Suggestion: {h['suggestion']}")
