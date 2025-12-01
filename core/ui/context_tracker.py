"""
Context Tracker - Token counting and context window monitoring.

Tracks total tokens used by HQ conversation to prevent exceeding 200K limit.
Provides warnings and manual compaction control.

Uses rough estimation (4 chars per token) - good enough for UI display.
For exact billing, use tiktoken library (future enhancement).
"""

from pathlib import Path
from typing import List, Dict, Optional


class ContextTracker:
    """
    Track token usage for context window management.

    Key responsibilities:
    - Estimate tokens from conversation + files
    - Calculate percentage of 200K limit
    - Provide warnings at 80% threshold
    - Support manual compaction

    Example:
        tracker = ContextTracker(max_tokens=200000)
        tracker.add_conversation(messages)
        tracker.add_file_content(latest_md)

        if tracker.should_warn():
            print(f"Context at {tracker.percentage()}%")
    """

    def __init__(self, max_tokens: int = 200000):
        """
        Initialize context tracker.

        Args:
            max_tokens: Maximum context window (default: 200K for Claude Sonnet)
        """
        self.max_tokens = max_tokens
        self.token_counts = {
            "conversation": 0,
            "latest_md": 0,
            "critical_analysis_md": 0,
            "user_context_md": 0,
            "other": 0
        }

    def add_conversation(self, messages: List[Dict[str, str]]) -> None:
        """
        Add conversation token count.

        Args:
            messages: List of chat messages
        """
        total_chars = sum(len(msg["content"]) for msg in messages)
        self.token_counts["conversation"] = self._estimate_tokens(total_chars)

    def add_file_content(self, name: str, content: str) -> None:
        """
        Add file content token count.

        Args:
            name: File category (latest_md, critical_analysis_md, user_context_md, other)
            content: File content
        """
        if name in self.token_counts:
            self.token_counts[name] = self._estimate_tokens(len(content))
        else:
            self.token_counts["other"] += self._estimate_tokens(len(content))

    def total_tokens(self) -> int:
        """
        Get total estimated tokens.

        Returns:
            Total token count across all sources
        """
        return sum(self.token_counts.values())

    def percentage(self) -> float:
        """
        Get percentage of context window used.

        Returns:
            Percentage (0-100)
        """
        return (self.total_tokens() / self.max_tokens) * 100

    def should_warn(self, threshold: float = 80.0) -> bool:
        """
        Check if should warn user about approaching limit.

        Args:
            threshold: Warning threshold percentage (default: 80%)

        Returns:
            True if over threshold
        """
        return self.percentage() >= threshold

    def remaining_tokens(self) -> int:
        """
        Get remaining tokens before hitting limit.

        Returns:
            Number of tokens remaining
        """
        return max(0, self.max_tokens - self.total_tokens())

    def breakdown(self) -> Dict[str, int]:
        """
        Get token breakdown by source.

        Returns:
            Dict mapping source to token count
        """
        return self.token_counts.copy()

    def can_compact(self, messages: List[Dict[str, str]], keep_recent: int = 15) -> bool:
        """
        Check if conversation can be compacted.

        Args:
            messages: List of chat messages
            keep_recent: Number of recent messages to keep verbatim

        Returns:
            True if there are enough messages to compact
        """
        return len(messages) > keep_recent + 5  # Need at least 5 messages to summarize

    def estimate_compaction_savings(self, messages: List[Dict[str, str]], keep_recent: int = 15) -> int:
        """
        Estimate token savings from compaction.

        Args:
            messages: List of chat messages
            keep_recent: Number of recent messages to keep verbatim

        Returns:
            Estimated tokens saved (rough estimate: ~70% reduction of old messages)
        """
        if not self.can_compact(messages, keep_recent):
            return 0

        # Messages to summarize
        old_messages = messages[:-keep_recent]
        old_chars = sum(len(msg["content"]) for msg in old_messages)
        old_tokens = self._estimate_tokens(old_chars)

        # Assume summary is ~30% of original (70% savings)
        return int(old_tokens * 0.7)

    def _estimate_tokens(self, char_count: int) -> int:
        """
        Estimate tokens from character count.

        Uses rule of thumb: 1 token ~= 4 characters (English text).

        For exact counts, use tiktoken library (future enhancement).

        Args:
            char_count: Number of characters

        Returns:
            Estimated token count
        """
        return max(1, char_count // 4)

    def reset(self) -> None:
        """Reset all token counts."""
        self.token_counts = {
            "conversation": 0,
            "latest_md": 0,
            "critical_analysis_md": 0,
            "user_context_md": 0,
            "other": 0
        }

    def format_display(self) -> str:
        """
        Format for UI display.

        Returns:
            Formatted string: "45K / 200K (22.5%)"
        """
        total = self.total_tokens()
        pct = self.percentage()

        # Format with K suffix
        if total >= 1000:
            total_str = f"{total // 1000}K"
        else:
            total_str = str(total)

        max_str = f"{self.max_tokens // 1000}K"

        return f"{total_str} / {max_str} ({pct:.1f}%)"

    def format_progress_bar(self, width: int = 20) -> str:
        """
        Format as progress bar for terminal display.

        Args:
            width: Progress bar width in characters

        Returns:
            Progress bar string: "[████████░░░░░░░░░░░░]"
        """
        pct = self.percentage() / 100
        filled = int(width * pct)
        empty = width - filled

        return f"[{'█' * filled}{'░' * empty}]"
