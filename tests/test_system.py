"""
Simple test script to verify the multi-agent system is working correctly.
This tests individual agents without requiring API calls.
"""

from backend.agents.syntax_checker import SyntaxCheckerAgent
from backend.agents.hallucination_detector import HallucinationDetectorAgent


def test_syntax_checker():
    """Test the Syntax Checker Agent"""
    print("="*80)
    print("Testing Syntax Checker Agent")
    print("="*80)

    agent = SyntaxCheckerAgent()

    # Test 1: Valid code
    print("\n1. Testing valid code...")
    valid_code = """
def calculate_sum(a: int, b: int) -> int:
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b
"""
    result = agent.validate(valid_code)
    assert result["status"] == "SYNTAX_VALID", "Valid code should pass"
    print("   [PASS] Valid code test passed")

    # Test 2: Invalid code (missing colon)
    print("\n2. Testing invalid code (missing colon)...")
    invalid_code = """
def greet(name)
    return f"Hello, {name}"
"""
    result = agent.validate(invalid_code)
    assert result["status"] == "SYNTAX_ERROR", "Invalid code should fail"
    assert len(result.get("errors", [])) > 0, "Should have errors"
    print("   [PASS] Invalid code detection passed")

    # Test 3: Invalid code (unclosed parenthesis)
    print("\n3. Testing invalid code (unclosed parenthesis)...")
    invalid_code2 = """
def calculate(x, y):
    result = max(x, y
    return result
"""
    result = agent.validate(invalid_code2)
    assert result["status"] == "SYNTAX_ERROR", "Invalid code should fail"
    print("   [PASS] Unclosed parenthesis detection passed")

    print("\n[SUCCESS] All Syntax Checker tests passed!\n")


def test_hallucination_detector():
    """Test the Hallucination Detector Agent"""
    print("="*80)
    print("Testing Hallucination Detector Agent")
    print("="*80)

    agent = HallucinationDetectorAgent()

    # Test 1: Valid imports (stdlib)
    print("\n1. Testing valid stdlib imports...")
    valid_code = """
import os
import json
from pathlib import Path
from typing import Dict, List
"""
    result = agent.verify(valid_code)
    assert result["status"] == "VERIFIED", "Valid imports should pass"
    print("   ✓ Valid stdlib imports test passed")

    # Test 2: Invalid imports (hallucinated module)
    print("\n2. Testing hallucinated module...")
    invalid_code = """
import os
import fake_module_that_does_not_exist_12345
"""
    result = agent.verify(invalid_code)
    assert result["status"] == "HALLUCINATION_DETECTED", "Hallucinated module should be detected"
    assert len(result.get("hallucinations", [])) > 0, "Should have hallucinations"
    print("   ✓ Hallucination detection passed")

    # Test 3: Mixed valid and invalid
    print("\n3. Testing mixed imports...")
    mixed_code = """
import os
import json
import totally_fake_module
from pathlib import Path
"""
    result = agent.verify(mixed_code)
    assert result["status"] == "HALLUCINATION_DETECTED", "Should detect the fake module"
    hallucinations = result.get("hallucinations", [])
    assert len(hallucinations) == 1, "Should have exactly 1 hallucination"
    print("   ✓ Mixed imports test passed")

    print("\n✅ All Hallucination Detector tests passed!\n")


def test_project_structure():
    """Verify project structure is correct"""
    print("="*80)
    print("Verifying Project Structure")
    print("="*80)

    import os
    import sys

    # Check main files
    files_to_check = [
        "orchestrator.py",
        "example.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "agents/__init__.py",
        "agents/code_generator/__init__.py",
        "agents/code_generator/agent.py",
        "agents/code_generator/CLAUDE.md",
        "agents/syntax_checker/__init__.py",
        "agents/syntax_checker/agent.py",
        "agents/syntax_checker/CLAUDE.md",
        "agents/hallucination_detector/__init__.py",
        "agents/hallucination_detector/agent.py",
        "agents/hallucination_detector/CLAUDE.md",
        "agents/code_reviewer/__init__.py",
        "agents/code_reviewer/agent.py",
        "agents/code_reviewer/CLAUDE.md",
        "agents/orchestrator/CLAUDE.md"
    ]

    print("\nChecking for required files...")
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} - MISSING!")
            all_exist = False

    if all_exist:
        print("\n✅ All required files present!\n")
    else:
        print("\n❌ Some files are missing!\n")
        sys.exit(1)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("Multi-Agent System - Test Suite")
    print("="*80 + "\n")

    try:
        # Test project structure
        test_project_structure()

        # Test individual agents
        test_syntax_checker()
        test_hallucination_detector()

        # Summary
        print("="*80)
        print("ALL TESTS PASSED! ✅")
        print("="*80)
        print("\nThe multi-agent system is ready to use!")
        print("\nNext steps:")
        print("1. Set up your .env file with ANTHROPIC_API_KEY")
        print("2. Run: python example.py")
        print("3. Start generating code with the orchestrator!")
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import sys
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
