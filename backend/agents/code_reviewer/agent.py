"""
Code Reviewer Agent
Provides comprehensive code review for quality, security, and maintainability.
Supports both Claude (Anthropic) and Ollama (local models).
"""

import re
from typing import Dict, Any, List
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CodeReviewerAgent:
    """
    Generic Code Review Agent that provides comprehensive code analysis.

    Reviews code for:
    - Correctness and logic
    - Security vulnerabilities
    - Performance issues
    - Maintainability
    - Best practices

    Supports both Claude (Anthropic) and Ollama (local models).
    """

    def __init__(self, model: str = None):
        """
        Initialize the Code Reviewer Agent.

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

    def review(self, code: str, requirements: str = "", focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Review code and provide comprehensive feedback.

        Args:
            code: Python code to review
            requirements: Original requirements (optional)
            focus_areas: Specific areas to focus on (optional)

        Returns:
            Dictionary with review results
        """
        if focus_areas is None:
            focus_areas = ["correctness", "security", "performance", "maintainability"]

        # Build review prompt
        prompt = "Please review the following Python code:\n\n"
        prompt += f"```python\n{code}\n```\n\n"

        if requirements:
            prompt += f"**Original Requirements**: {requirements}\n\n"

        prompt += f"**Focus Areas**: {', '.join(focus_areas)}\n\n"
        prompt += "Provide a comprehensive code review following the structured format in your instructions."

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

            # Parse the review
            parsed_review = self._parse_review(content)

            return {
                "status": "success",
                "raw_review": content,
                **parsed_review
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _parse_review(self, review_text: str) -> Dict[str, Any]:
        """Parse structured review from Claude's response"""
        result = {
            "summary": "",
            "score": None,
            "critical_issues": [],
            "major_concerns": [],
            "minor_suggestions": [],
            "positive_highlights": [],
            "checklist": {},
            "action_items": []
        }

        # Extract overall assessment/summary
        if "## Overall Assessment" in review_text or "### Overall Assessment" in review_text:
            pattern = r"## Overall Assessment\s*\n(.*?)(?=\n##|\n###|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                result["summary"] = match.group(1).strip()

        # Extract score
        score_pattern = r"Score[:\s]+(\d+(?:\.\d+)?)\s*/\s*10"
        score_match = re.search(score_pattern, review_text, re.IGNORECASE)
        if score_match:
            result["score"] = float(score_match.group(1))

        # Extract critical issues (🔴)
        if "## Critical Issues" in review_text:
            pattern = r"## Critical Issues.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                issues_text = match.group(1)
                issues = self._extract_issues(issues_text)
                result["critical_issues"] = issues

        # Extract major concerns (🟠)
        if "## Major Concerns" in review_text:
            pattern = r"## Major Concerns.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                concerns_text = match.group(1)
                concerns = self._extract_issues(concerns_text)
                result["major_concerns"] = concerns

        # Extract minor suggestions (🟡)
        if "## Minor Suggestions" in review_text:
            pattern = r"## Minor Suggestions.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                suggestions_text = match.group(1)
                # Extract bullet points
                suggestions = re.findall(r"[-•*]\s*(.+)", suggestions_text)
                result["minor_suggestions"] = [s.strip() for s in suggestions]

        # Extract positive highlights (🟢)
        if "## Positive Highlights" in review_text:
            pattern = r"## Positive Highlights.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                highlights_text = match.group(1)
                highlights = re.findall(r"[-•*]\s*(.+)", highlights_text)
                result["positive_highlights"] = [h.strip() for h in highlights]

        # Extract checklist
        if "## Checklist" in review_text:
            pattern = r"## Checklist.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                checklist_text = match.group(1)
                checklist_items = re.findall(r"\|\s*(\w+)\s*\|\s*([✅⚠️❌]+)", checklist_text)
                for category, status in checklist_items:
                    result["checklist"][category] = status

        # Extract action items
        if "## Action Items" in review_text:
            pattern = r"## Action Items.*?\n(.*?)(?=\n##|$)"
            match = re.search(pattern, review_text, re.DOTALL)
            if match:
                actions_text = match.group(1)
                actions = re.findall(r"\d+\.\s*\[[ x]\]\s*(.+)", actions_text)
                result["action_items"] = [a.strip() for a in actions]

        return result

    def _extract_issues(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured issues from text"""
        issues = []

        # Pattern for issues with structured format
        issue_pattern = r"###\s*Issue\s*\d+:?\s*(.+?)\n.*?-\s*\*\*Location\*\*:\s*(.+?)\n.*?-\s*\*\*Problem\*\*:\s*(.+?)\n.*?-\s*\*\*(?:Impact|Recommendation)\*\*:\s*(.+?)(?=\n###|\n##|$)"

        matches = re.finditer(issue_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            issues.append({
                "title": match.group(1).strip(),
                "location": match.group(2).strip(),
                "problem": match.group(3).strip(),
                "recommendation": match.group(4).strip()
            })

        return issues


if __name__ == "__main__":
    # Example usage
    agent = CodeReviewerAgent()

    # Test code
    test_code = """
def get_user(id):
    query = f"SELECT * FROM users WHERE id = {id}"
    result = db.execute(query)
    return result[0] if result else None
"""

    result = agent.review(
        code=test_code,
        requirements="Create a function to retrieve a user by ID",
        focus_areas=["security", "correctness"]
    )

    if result["status"] == "success":
        print("Code Review:")
        print(f"Score: {result.get('score', 'N/A')}/10")
        print(f"\nSummary: {result.get('summary', 'N/A')}")

        if result.get("critical_issues"):
            print(f"\nCritical Issues: {len(result['critical_issues'])}")
            for issue in result["critical_issues"]:
                print(f"  - {issue.get('title', 'Unknown')}")
    else:
        print(f"Error: {result['error']}")
