"""
Multi-Agent Code Generation System - Orchestrator
Coordinates workflow between specialized agents for code generation and validation.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .agents.code_generator import CodeGeneratorAgent
from .agents.syntax_checker import SyntaxCheckerAgent
from .agents.hallucination_detector import HallucinationDetectorAgent
from .agents.code_reviewer import CodeReviewerAgent


class Stage(Enum):
    """Pipeline stages"""
    INITIALIZED = "initialized"
    CODE_GENERATION = "code_generation"
    SYNTAX_CHECK = "syntax_check"
    HALLUCINATION_CHECK = "hallucination_check"
    CODE_REVIEW = "code_review"
    COMPLETED = "completed"
    FAILED = "failed"


class Status(Enum):
    """Request status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RequestState:
    """Track state for each code generation request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_request: str = ""
    current_stage: Stage = Stage.INITIALIZED
    status: Status = Status.IN_PROGRESS
    attempts: Dict[str, int] = field(default_factory=lambda: {
        "generation": 0,
        "syntax_fix": 0,
        "hallucination_fix": 0
    })
    artifacts: Dict[str, Any] = field(default_factory=lambda: {
        "generated_code": None,
        "syntax_result": None,
        "hallucination_result": None,
        "review_result": None
    })
    error_messages: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        data = asdict(self)
        data['current_stage'] = self.current_stage.value
        data['status'] = self.status.value
        return data


class Orchestrator:
    """
    Main orchestrator that coordinates the multi-agent pipeline.

    Pipeline Flow:
    1. Code Generation
    2. Syntax Validation (with retries)
    3. Hallucination Detection (with retries)
    4. Code Review (optional)
    """

    # Configuration
    MAX_GENERATION_RETRIES = 3
    MAX_SYNTAX_RETRIES = 3
    MAX_HALLUCINATION_RETRIES = 3
    MAX_TOTAL_RETRIES = 5

    def __init__(self, enable_code_review: bool = True, verbose: bool = True):
        """
        Initialize the orchestrator with all agents.

        Args:
            enable_code_review: Whether to include code review step
            verbose: Whether to print detailed logs
        """
        self.enable_code_review = enable_code_review
        self.verbose = verbose

        # Initialize agents
        self.code_generator = CodeGeneratorAgent()
        self.syntax_checker = SyntaxCheckerAgent()
        self.hallucination_detector = HallucinationDetectorAgent()
        self.code_reviewer = CodeReviewerAgent() if enable_code_review else None

        # State tracking
        self.states: Dict[str, RequestState] = {}

        self._log("Orchestrator initialized successfully")

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def generate_code(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point for code generation pipeline.

        Args:
            user_request: User's natural language code request

        Returns:
            Dictionary containing final results and validation status
        """
        # Create new request state
        state = RequestState(user_request=user_request)
        self.states[state.request_id] = state

        self._log(f"Starting new request: {state.request_id}")
        self._log(f"User request: {user_request}")

        try:
            # Stage 1: Code Generation
            if not self._run_code_generation(state):
                return self._compile_failure_response(state)

            # Stage 2: Syntax Validation
            if not self._run_syntax_validation(state):
                return self._compile_failure_response(state)

            # Stage 3: Hallucination Detection
            if not self._run_hallucination_detection(state):
                return self._compile_failure_response(state)

            # Stage 4: Code Review (optional)
            if self.enable_code_review:
                self._run_code_review(state)

            # Mark as completed
            state.status = Status.COMPLETED
            state.current_stage = Stage.COMPLETED

            return self._compile_success_response(state)

        except Exception as e:
            self._log(f"Unexpected error: {str(e)}", level="ERROR")
            state.status = Status.FAILED
            state.current_stage = Stage.FAILED
            state.error_messages.append(f"Unexpected error: {str(e)}")
            return self._compile_failure_response(state)

    def _run_code_generation(self, state: RequestState) -> bool:
        """
        Run code generation with retries.

        Returns:
            True if successful, False otherwise
        """
        state.current_stage = Stage.CODE_GENERATION
        self._log("Stage 1: Code Generation")

        for attempt in range(1, self.MAX_GENERATION_RETRIES + 1):
            state.attempts["generation"] = attempt
            self._log(f"  Attempt {attempt}/{self.MAX_GENERATION_RETRIES}")

            try:
                # Prepare request
                request_data = {
                    "action": "generate",
                    "request": state.user_request,
                    "constraints": ["python_only", "no_placeholders"]
                }

                # Add feedback if retry
                if attempt > 1 and state.error_messages:
                    request_data["previous_attempt"] = state.artifacts["generated_code"]
                    request_data["feedback"] = state.error_messages[-1]

                # Generate code
                result = self.code_generator.generate(request_data)

                if result["status"] == "success":
                    state.artifacts["generated_code"] = result["code"]
                    self._log("  ✓ Code generated successfully")
                    return True
                else:
                    error_msg = result.get("error", "Unknown error")
                    state.error_messages.append(f"Generation error: {error_msg}")
                    self._log(f"  ✗ Generation failed: {error_msg}", level="WARN")

            except Exception as e:
                error_msg = f"Generation exception: {str(e)}"
                state.error_messages.append(error_msg)
                self._log(f"  ✗ {error_msg}", level="ERROR")

        self._log("  ✗ Max generation retries exceeded", level="ERROR")
        return False

    def _run_syntax_validation(self, state: RequestState) -> bool:
        """
        Run syntax validation with retries.

        Returns:
            True if syntax is valid, False otherwise
        """
        state.current_stage = Stage.SYNTAX_CHECK
        self._log("Stage 2: Syntax Validation")

        for attempt in range(1, self.MAX_SYNTAX_RETRIES + 1):
            state.attempts["syntax_fix"] = attempt
            self._log(f"  Attempt {attempt}/{self.MAX_SYNTAX_RETRIES}")

            try:
                # Validate syntax
                result = self.syntax_checker.validate(
                    state.artifacts["generated_code"],
                    context=f"Generated for: {state.user_request}"
                )

                state.artifacts["syntax_result"] = result

                if result["status"] == "SYNTAX_VALID":
                    self._log("  ✓ Syntax validation passed")
                    return True
                else:
                    # Syntax errors found - try to regenerate with feedback
                    self._log(f"  ✗ Syntax errors found: {len(result.get('errors', []))} error(s)", level="WARN")

                    # Use corrected code if available
                    if "corrected_code" in result and result["corrected_code"]:
                        state.artifacts["generated_code"] = result["corrected_code"]
                        self._log("  → Using auto-corrected code")
                    else:
                        # Regenerate with feedback
                        error_feedback = self._format_syntax_errors(result)
                        state.error_messages.append(error_feedback)

                        if not self._run_code_generation(state):
                            return False

            except Exception as e:
                error_msg = f"Syntax validation exception: {str(e)}"
                state.error_messages.append(error_msg)
                self._log(f"  ✗ {error_msg}", level="ERROR")

        self._log("  ✗ Max syntax validation retries exceeded", level="ERROR")
        return False

    def _run_hallucination_detection(self, state: RequestState) -> bool:
        """
        Run hallucination detection with retries.

        Returns:
            True if no hallucinations found, False otherwise
        """
        state.current_stage = Stage.HALLUCINATION_CHECK
        self._log("Stage 3: Hallucination Detection")

        for attempt in range(1, self.MAX_HALLUCINATION_RETRIES + 1):
            state.attempts["hallucination_fix"] = attempt
            self._log(f"  Attempt {attempt}/{self.MAX_HALLUCINATION_RETRIES}")

            try:
                # Detect hallucinations
                result = self.hallucination_detector.verify(
                    state.artifacts["generated_code"]
                )

                state.artifacts["hallucination_result"] = result

                if result["status"] == "VERIFIED":
                    self._log("  ✓ All references verified")
                    return True
                else:
                    # Hallucinations found - regenerate with feedback
                    hallucination_count = len(result.get("hallucinations", []))
                    self._log(f"  ✗ Hallucinations detected: {hallucination_count} issue(s)", level="WARN")

                    error_feedback = self._format_hallucination_errors(result)
                    state.error_messages.append(error_feedback)

                    if not self._run_code_generation(state):
                        return False

            except Exception as e:
                error_msg = f"Hallucination detection exception: {str(e)}"
                state.error_messages.append(error_msg)
                self._log(f"  ✗ {error_msg}", level="ERROR")

        self._log("  ✗ Max hallucination detection retries exceeded", level="ERROR")
        return False

    def _run_code_review(self, state: RequestState):
        """
        Run code review (non-blocking).
        """
        state.current_stage = Stage.CODE_REVIEW
        self._log("Stage 4: Code Review (optional)")

        try:
            result = self.code_reviewer.review(
                code=state.artifacts["generated_code"],
                requirements=state.user_request
            )

            state.artifacts["review_result"] = result
            self._log(f"  ✓ Code review completed (Score: {result.get('score', 'N/A')}/10)")

        except Exception as e:
            self._log(f"  ⚠ Code review failed: {str(e)}", level="WARN")
            state.artifacts["review_result"] = {
                "status": "error",
                "error": str(e)
            }

    def _format_syntax_errors(self, result: Dict[str, Any]) -> str:
        """Format syntax errors for feedback to code generator"""
        errors = result.get("errors", [])
        feedback = "Syntax Errors Found:\n"
        for i, error in enumerate(errors, 1):
            feedback += f"{i}. Line {error.get('line', '?')}: {error.get('issue', 'Unknown issue')}\n"
            feedback += f"   Fix: {error.get('fix', 'No suggestion')}\n"
        return feedback

    def _format_hallucination_errors(self, result: Dict[str, Any]) -> str:
        """Format hallucination errors for feedback to code generator"""
        hallucinations = result.get("hallucinations", [])
        feedback = "Hallucinations Detected:\n"
        for i, h in enumerate(hallucinations, 1):
            feedback += f"{i}. {h.get('type', 'Unknown')}: {h.get('referenced', 'Unknown')}\n"
            feedback += f"   Issue: {h.get('issue', 'Does not exist')}\n"
            feedback += f"   Suggestion: {h.get('suggestion', 'Remove or replace')}\n"
        return feedback

    def _compile_success_response(self, state: RequestState) -> Dict[str, Any]:
        """Compile final success response"""
        response = {
            "request_id": state.request_id,
            "status": "success",
            "code": state.artifacts["generated_code"],
            "validation": {
                "syntax": {
                    "status": "✅ Valid",
                    "details": "Python syntax validated successfully"
                },
                "hallucination": {
                    "status": "✅ Verified",
                    "details": "All imports and functions verified"
                }
            },
            "metadata": {
                "total_attempts": sum(state.attempts.values()),
                "generation_attempts": state.attempts["generation"],
                "syntax_fix_attempts": state.attempts["syntax_fix"],
                "hallucination_fix_attempts": state.attempts["hallucination_fix"],
                "created_at": state.created_at,
                "completed_at": datetime.now().isoformat()
            }
        }

        # Add review if available
        if state.artifacts.get("review_result"):
            review = state.artifacts["review_result"]
            response["validation"]["review"] = {
                "status": "✅ Completed",
                "score": review.get("score", "N/A"),
                "summary": review.get("summary", "")
            }
            response["review_details"] = review

        return response

    def _compile_failure_response(self, state: RequestState) -> Dict[str, Any]:
        """Compile failure response"""
        return {
            "request_id": state.request_id,
            "status": "failed",
            "error": "Failed to generate valid code",
            "errors": state.error_messages,
            "last_attempt": state.artifacts.get("generated_code"),
            "metadata": {
                "failed_at_stage": state.current_stage.value,
                "total_attempts": sum(state.attempts.values()),
                "generation_attempts": state.attempts["generation"],
                "syntax_fix_attempts": state.attempts["syntax_fix"],
                "hallucination_fix_attempts": state.attempts["hallucination_fix"],
                "created_at": state.created_at,
                "failed_at": datetime.now().isoformat()
            }
        }

    def get_state(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get state for a specific request"""
        if request_id in self.states:
            return self.states[request_id].to_dict()
        return None

    def format_response(self, response: Dict[str, Any]) -> str:
        """Format response as markdown for display"""
        if response["status"] == "success":
            return self._format_success_markdown(response)
        else:
            return self._format_failure_markdown(response)

    def _format_success_markdown(self, response: Dict[str, Any]) -> str:
        """Format success response as markdown"""
        md = "# Generated Code\n\n"
        md += "```python\n"
        md += response["code"]
        md += "\n```\n\n"

        md += "## Validation Status\n\n"
        md += "| Check | Status | Details |\n"
        md += "|-------|--------|---------||\n"
        md += f"| Syntax | {response['validation']['syntax']['status']} | {response['validation']['syntax']['details']} |\n"
        md += f"| Hallucination | {response['validation']['hallucination']['status']} | {response['validation']['hallucination']['details']} |\n"

        if "review" in response["validation"]:
            review = response["validation"]["review"]
            md += f"| Code Review | {review['status']} | Score: {review['score']}/10 |\n"

        md += "\n## Metadata\n\n"
        md += f"- Total Attempts: {response['metadata']['total_attempts']}\n"
        md += f"- Request ID: {response['request_id']}\n"

        return md

    def _format_failure_markdown(self, response: Dict[str, Any]) -> str:
        """Format failure response as markdown"""
        md = "# Code Generation Failed\n\n"
        md += f"**Error**: {response['error']}\n\n"

        md += "## Error Details\n\n"
        for i, error in enumerate(response['errors'], 1):
            md += f"{i}. {error}\n"

        md += "\n## Metadata\n\n"
        md += f"- Failed at Stage: {response['metadata']['failed_at_stage']}\n"
        md += f"- Total Attempts: {response['metadata']['total_attempts']}\n"
        md += f"- Request ID: {response['request_id']}\n"

        if response.get("last_attempt"):
            md += "\n## Last Attempt\n\n"
            md += "```python\n"
            md += response["last_attempt"]
            md += "\n```\n"

        return md


if __name__ == "__main__":
    # Example usage
    orchestrator = Orchestrator(enable_code_review=True, verbose=True)

    # Test request
    request = "Create a function to read a JSON file and return its contents as a dictionary"

    result = orchestrator.generate_code(request)
    print("\n" + "="*80)
    print(orchestrator.format_response(result))
