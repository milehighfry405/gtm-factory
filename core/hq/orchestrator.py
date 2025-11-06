"""
HQ Orchestrator: Socratic conversation handler with streaming responses.

This module implements the conversational layer of the GTM Factory system,
conducting Socratic questioning to extract user intent before planning research drops.

Based on Anthropic's orchestrator-workers pattern and streaming API best practices.
"""

from typing import Optional, Dict, Any, Generator, List
from pathlib import Path
import json
from datetime import datetime

import anthropic


class HQOrchestrator:
    """
    Main orchestrator for GTM Factory research sessions.

    Responsibilities:
    - Conduct Socratic questioning to clarify user intent
    - Extract strategic WHY from conversation
    - Plan research drops (1-4 researchers per drop)
    - Coordinate with memory manager for persistence
    - Synthesize findings into living truth documents

    Attributes:
        client: Anthropic API client for Claude interactions
        model: Claude model identifier (default: claude-sonnet-4-5)
        system_prompt: XML-tagged system prompt defining orchestrator behavior
        conversation_history: List of message dicts (role, content)
        project_path: Path to current project directory
        session_id: Current session identifier
    """

    def __init__(
        self,
        api_key: str,
        project_path: Path,
        session_id: str,
        model: str = "claude-sonnet-4-5"
    ):
        """
        Initialize HQ Orchestrator with project context.

        Args:
            api_key: Anthropic API key for Claude access
            project_path: Absolute path to /projects/{company-name}/
            session_id: Session identifier (e.g., "session-1-hypothesis")
            model: Claude model to use (default: claude-sonnet-4-5)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.project_path = Path(project_path)
        self.session_id = session_id
        self.conversation_history: List[Dict[str, str]] = []

        # Load system prompt from prompts/hq-orchestrator.md
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        Load and format system prompt with XML tags.

        Returns structured prompt following Anthropic's best practices:
        - XML tags for clarity
        - Role, job, inputs, outputs, constraints sections
        - Examples and critical rules

        Returns:
            Formatted system prompt string
        """
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "hq-orchestrator.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt not found at {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        # Wrap in XML tags for structured prompting
        return f"""<role>
{base_prompt}
</role>

<context>
Project Path: {self.project_path}
Session ID: {self.session_id}
Current Date: {datetime.now().strftime('%Y-%m-%d')}
</context>"""

    def chat_stream(
        self,
        user_message: str,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """
        Send user message and stream Claude's response in real-time.

        Implements Anthropic's streaming API pattern using context manager.
        Yields text chunks as they arrive for immediate display to user.

        Args:
            user_message: User's input message
            max_tokens: Maximum tokens for response (default: 4096)

        Yields:
            Text chunks from Claude's streaming response

        Example:
            >>> orchestrator = HQOrchestrator(api_key, project_path, "session-1")
            >>> for chunk in orchestrator.chat_stream("Research Arthur.ai"):
            ...     print(chunk, end="", flush=True)
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Stream response from Claude
        assistant_message = ""

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=self.conversation_history
            ) as stream:
                for text in stream.text_stream:
                    assistant_message += text
                    yield text

        except anthropic.APIError as e:
            error_msg = f"API Error: {str(e)}"
            yield error_msg
            assistant_message = error_msg

        finally:
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

    def chat(
        self,
        user_message: str,
        max_tokens: int = 4096
    ) -> str:
        """
        Send user message and get complete response (non-streaming).

        Use this for programmatic interactions where streaming isn't needed.
        For user-facing chat, prefer chat_stream() for better UX.

        Args:
            user_message: User's input message
            max_tokens: Maximum tokens for response (default: 4096)

        Returns:
            Complete assistant response as string
        """
        # Collect all chunks from stream
        response = "".join(self.chat_stream(user_message, max_tokens))
        return response

    def extract_drop_plan(self) -> Optional[Dict[str, Any]]:
        """
        Extract research drop plan from conversation.

        Analyzes conversation history to identify when user is ready for research,
        then requests structured drop plan JSON from Claude.

        Returns:
            Drop plan dict with keys: drop_id, hypothesis, researchers_assigned, etc.
            None if user is not ready for research yet.

        Expected structure:
            {
                "drop_id": "drop-1",
                "hypothesis": "Brief hypothesis statement",
                "researchers_assigned": [
                    {
                        "researcher_type": "general-researcher",
                        "focus_question": "Specific question",
                        "token_budget": 4000,
                        ...
                    }
                ]
            }
        """
        # Request drop plan from Claude
        plan_request = """Based on our conversation, please create a research drop plan.

If the user is ready for research (intent is clear), respond with a JSON drop plan.
If more clarification is needed, respond with "NEEDS_CLARIFICATION" and ask more questions.

Format your response as either:
1. Valid JSON matching the drop plan schema (see system prompt)
2. The string "NEEDS_CLARIFICATION" followed by your questions"""

        response = self.chat(plan_request, max_tokens=2048)

        # Check if more clarification needed
        if "NEEDS_CLARIFICATION" in response:
            return None

        # Try to parse JSON from response
        try:
            # Extract JSON from response (handles markdown code blocks)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                return None

            plan_json = response[json_start:json_end]
            drop_plan = json.loads(plan_json)

            return drop_plan

        except (json.JSONDecodeError, ValueError):
            # Failed to parse - treat as clarification needed
            return None

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get full conversation history for persistence.

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        return self.conversation_history

    def load_conversation_history(self, history: List[Dict[str, str]]) -> None:
        """
        Load conversation history from persistence.

        Useful for resuming sessions or context management.

        Args:
            history: List of message dicts with 'role' and 'content' keys
        """
        self.conversation_history = history

    def reset_conversation(self) -> None:
        """Reset conversation history to start fresh."""
        self.conversation_history = []
