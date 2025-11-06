"""
Context Extractor: Strategic WHY extraction from conversations.

Analyzes conversation history to extract user's mental models, priorities,
constraints, and decision context. Creates user-context.md files that persist
with each research drop.

Based on Anthropic's context management and memory tool patterns.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import anthropic


@dataclass
class UserContext:
    """
    Structured representation of user's strategic context.

    Attributes:
        strategic_why: Why this research matters (business impact, decision gates)
        decision_context: What decision this research will inform
        mental_models: Frameworks, analogies user employs
        priorities: What matters most vs nice-to-have
        constraints: Budget, time, technical limitations
        success_criteria: What makes research valuable
        hypothesis: Core hypothesis being tested (if applicable)
        extracted_at: Timestamp of extraction
    """
    strategic_why: str
    decision_context: str
    mental_models: List[str]
    priorities: Dict[str, str]  # {"must_have": [...], "nice_to_have": [...]}
    constraints: List[str]
    success_criteria: str
    hypothesis: Optional[str] = None
    extracted_at: str = ""

    def __post_init__(self):
        """Set extraction timestamp if not provided."""
        if not self.extracted_at:
            self.extracted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_markdown(self) -> str:
        """
        Convert context to markdown format for user-context.md files.

        Returns:
            Formatted markdown string suitable for file persistence
        """
        md = f"""# User Context

**Extracted**: {self.extracted_at}

---

## Strategic WHY

{self.strategic_why}

---

## Decision Context

{self.decision_context}

---

## Success Criteria

{self.success_criteria}

---

## Mental Models

"""
        for model in self.mental_models:
            md += f"- {model}\n"

        md += "\n---\n\n## Priorities\n\n### Must Have\n\n"

        for priority in self.priorities.get("must_have", []):
            md += f"- {priority}\n"

        md += "\n### Nice to Have\n\n"

        for priority in self.priorities.get("nice_to_have", []):
            md += f"- {priority}\n"

        md += "\n---\n\n## Constraints\n\n"

        for constraint in self.constraints:
            md += f"- {constraint}\n"

        if self.hypothesis:
            md += f"\n---\n\n## Hypothesis\n\n{self.hypothesis}\n"

        return md


class ContextExtractor:
    """
    Extracts strategic WHY and user context from conversations.

    Uses Claude to analyze conversation history and identify:
    - Why research matters (strategic WHY)
    - What decision it informs
    - User's mental models and frameworks
    - Priorities and constraints
    - Success criteria

    Attributes:
        client: Anthropic API client
        model: Claude model identifier
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        """
        Initialize context extractor.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-sonnet-4-5)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def extract(
        self,
        conversation_history: List[Dict[str, str]],
        max_tokens: int = 2048
    ) -> UserContext:
        """
        Extract user context from conversation history.

        Analyzes conversation to identify strategic signals and user intent.
        Returns structured UserContext object.

        Args:
            conversation_history: List of message dicts (role, content)
            max_tokens: Maximum tokens for extraction (default: 2048)

        Returns:
            UserContext object with extracted strategic information

        Example:
            >>> extractor = ContextExtractor(api_key)
            >>> context = extractor.extract(conversation_history)
            >>> print(context.strategic_why)
        """
        # Build extraction prompt
        extraction_prompt = self._build_extraction_prompt(conversation_history)

        # Request extraction from Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self._get_system_prompt(),
            messages=[{
                "role": "user",
                "content": extraction_prompt
            }]
        )

        # Parse response into UserContext
        context = self._parse_context_response(response.content[0].text)

        return context

    def _get_system_prompt(self) -> str:
        """
        Get system prompt for context extraction.

        Defines extraction behavior following Anthropic's structured prompting.

        Returns:
            System prompt string with XML tags
        """
        return """<role>
You are a context extraction specialist. Your job is to analyze conversations and extract the user's strategic WHY, decision context, mental models, priorities, and constraints.

Focus on:
- **Strategic WHY**: Why does this research matter? (business impact, decision gates)
- **Decision Context**: What decision will this inform? (hire, build, buy, expand)
- **Mental Models**: Frameworks, analogies, patterns the user employs
- **Priorities**: What's "must have" vs "nice to have"
- **Constraints**: Budget, time, technical limitations mentioned
- **Success Criteria**: What makes research valuable to this user
- **Hypothesis**: Core hypothesis being tested (if mentioned)

Listen for signals:
- Reframings ("actually, what I mean is...")
- Emphasis ("the most important thing is...")
- Comparisons ("similar to...", "like...")
- Constraints ("we can't...", "we need to...")
- Outcomes ("this will help us...")

Output as structured JSON matching this schema:
{
  "strategic_why": "string",
  "decision_context": "string",
  "mental_models": ["string"],
  "priorities": {
    "must_have": ["string"],
    "nice_to_have": ["string"]
  },
  "constraints": ["string"],
  "success_criteria": "string",
  "hypothesis": "string or null"
}
</role>"""

    def _build_extraction_prompt(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Build extraction prompt from conversation history.

        Args:
            conversation_history: List of message dicts

        Returns:
            Formatted prompt string
        """
        # Convert conversation to readable format
        conversation_text = self._format_conversation(conversation_history)

        return f"""Analyze this conversation and extract the user's strategic context.

<conversation>
{conversation_text}
</conversation>

Extract and return a JSON object with the user's:
- strategic_why
- decision_context
- mental_models (list)
- priorities (must_have and nice_to_have lists)
- constraints (list)
- success_criteria
- hypothesis (if mentioned, else null)

Focus on what the user ACTUALLY cares about, not what they initially said."""

    def _format_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for prompt inclusion.

        Args:
            conversation_history: List of message dicts

        Returns:
            Formatted conversation string
        """
        formatted = []

        for msg in conversation_history:
            role = msg['role'].upper()
            content = msg['content']
            formatted.append(f"[{role}]: {content}")

        return "\n\n".join(formatted)

    def _parse_context_response(self, response_text: str) -> UserContext:
        """
        Parse Claude's response into UserContext object.

        Handles JSON extraction from markdown code blocks and raw JSON.

        Args:
            response_text: Raw response from Claude

        Returns:
            UserContext object

        Raises:
            ValueError: If response cannot be parsed into valid context
        """
        import json

        # Try to extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in context extraction response")

        json_str = response_text[json_start:json_end]

        try:
            context_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse context JSON: {e}")

        # Validate required fields
        required_fields = [
            'strategic_why',
            'decision_context',
            'mental_models',
            'priorities',
            'constraints',
            'success_criteria'
        ]

        for field in required_fields:
            if field not in context_dict:
                raise ValueError(f"Missing required field: {field}")

        # Create UserContext object
        return UserContext(
            strategic_why=context_dict['strategic_why'],
            decision_context=context_dict['decision_context'],
            mental_models=context_dict['mental_models'],
            priorities=context_dict['priorities'],
            constraints=context_dict['constraints'],
            success_criteria=context_dict['success_criteria'],
            hypothesis=context_dict.get('hypothesis')
        )
