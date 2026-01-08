"""
Example usage of the Multi-Agent Code Generation System
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend.orchestrator import Orchestrator
import json


def main():
    """Run example code generation requests"""

    print("="*80)
    print("Multi-Agent Code Generation System - Example")
    print("="*80)
    print()

    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = Orchestrator(enable_code_review=True, verbose=True)
    print()

    # Example requests
    examples = [
        {
            "name": "Example 1: JSON File Reader",
            "request": "Create a function to read a JSON file and return its contents as a dictionary with error handling"
        },
        {
            "name": "Example 2: Factorial Calculator",
            "request": "Write a function that calculates factorial using recursion with memoization for performance"
        },
        {
            "name": "Example 3: Data Validator",
            "request": "Create a function that validates email addresses using regex and returns True/False"
        }
    ]

    # Run each example
    for i, example in enumerate(examples, 1):
        print("\n" + "="*80)
        print(f"{example['name']}")
        print("="*80)
        print(f"Request: {example['request']}")
        print()

        # Generate code
        result = orchestrator.generate_code(example['request'])

        # Display results
        print("\n" + "-"*80)
        print("RESULT")
        print("-"*80)
        print(orchestrator.format_response(result))

        # Save detailed result to file
        output_filename = f"example_output_{i}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\nDetailed results saved to: {output_filename}")

        # Pause between examples (optional)
        if i < len(examples):
            input("\nPress Enter to continue to next example...")

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


def run_single_request():
    """Run a single custom request"""

    print("="*80)
    print("Multi-Agent Code Generation System - Single Request")
    print("="*80)
    print()

    # Get user input
    request = input("Enter your code generation request: ")

    if not request.strip():
        print("Error: Empty request")
        return

    # Initialize orchestrator
    orchestrator = Orchestrator(enable_code_review=True, verbose=True)

    # Generate code
    print("\nGenerating code...")
    result = orchestrator.generate_code(request)

    # Display results
    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    print(orchestrator.format_response(result))

    # Save to file
    with open('single_request_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print("\nDetailed results saved to: single_request_output.json")


def test_individual_agents():
    """Test individual agents separately"""

    print("="*80)
    print("Testing Individual Agents")
    print("="*80)
    print()

    # Test Code Generator
    print("1. Testing Code Generator Agent")
    print("-"*80)
    from backend.agents.code_generator import CodeGeneratorAgent

    gen_agent = CodeGeneratorAgent()
    gen_result = gen_agent.generate({
        "action": "generate",
        "request": "Create a simple calculator function for addition",
        "constraints": ["python_only"]
    })

    if gen_result["status"] == "success":
        print("✓ Code generated successfully")
        print(f"Code:\n{gen_result['code'][:200]}...")
    else:
        print(f"✗ Error: {gen_result['error']}")
    print()

    # Test Syntax Checker
    print("2. Testing Syntax Checker Agent")
    print("-"*80)
    from backend.agents.syntax_checker import SyntaxCheckerAgent

    syntax_agent = SyntaxCheckerAgent()

    valid_code = "def add(a, b):\n    return a + b"
    syntax_result = syntax_agent.validate(valid_code)

    print(f"Valid code check: {syntax_result['status']}")

    invalid_code = "def add(a, b)\n    return a + b"
    syntax_result = syntax_agent.validate(invalid_code)

    print(f"Invalid code check: {syntax_result['status']}")
    if syntax_result.get('errors'):
        print(f"Errors found: {len(syntax_result['errors'])}")
    print()

    # Test Hallucination Detector
    print("3. Testing Hallucination Detector Agent")
    print("-"*80)
    from backend.agents.hallucination_detector import HallucinationDetectorAgent

    hall_agent = HallucinationDetectorAgent()

    valid_imports = "import os\nimport json\nfrom pathlib import Path"
    hall_result = hall_agent.verify(valid_imports)

    print(f"Valid imports check: {hall_result['status']}")

    invalid_imports = "import os\nimport fake_module_12345"
    hall_result = hall_agent.verify(invalid_imports)

    print(f"Invalid imports check: {hall_result['status']}")
    if hall_result.get('hallucinations'):
        print(f"Hallucinations found: {len(hall_result['hallucinations'])}")
    print()

    # Test Code Reviewer
    print("4. Testing Code Reviewer Agent")
    print("-"*80)
    from backend.agents.code_reviewer import CodeReviewerAgent

    review_agent = CodeReviewerAgent()

    test_code = """
def divide(a, b):
    return a / b
"""

    review_result = review_agent.review(test_code, "Create a division function")

    if review_result["status"] == "success":
        print(f"✓ Code reviewed successfully")
        print(f"Score: {review_result.get('score', 'N/A')}/10")
    else:
        print(f"✗ Error: {review_result['error']}")

    print("\n" + "="*80)
    print("Individual agent tests completed!")
    print("="*80)


if __name__ == "__main__":
    import sys

    print("Multi-Agent Code Generation System")
    print()
    print("Choose an option:")
    print("1. Run example requests")
    print("2. Run single custom request")
    print("3. Test individual agents")
    print("4. Exit")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        main()
    elif choice == "2":
        run_single_request()
    elif choice == "3":
        test_individual_agents()
    elif choice == "4":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)
