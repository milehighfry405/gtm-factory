"""
Latest Generator - Synthesizes research outputs into living truth documents.

Follows Anthropic's synthesis patterns:
- Iterative synthesis (incremental updates, not single-shot)
- Token-efficient (compress context, just-in-time loading)
- Structured prompts (XML tags for clarity)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LatestGenerator:
    """
    Generates and updates `latest.md` files by synthesizing research outputs.

    Uses iterative synthesis pattern from Anthropic's multi-agent research system:
    - Load existing latest.md (compacted state)
    - Add new drop findings incrementally
    - Detect contradictions
    - Apply invalidations (strikethrough)
    - Save updated latest.md

    Example:
        generator = LatestGenerator()
        latest_md = generator.synthesize_drop(
            session_path=Path("projects/demo-company/sessions/session-1"),
            drop_id="drop-1"
        )
    """

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize Latest Generator.

        Args:
            model: OpenAI model for synthesis (default: gpt-4o)
                   TODO: Switch to gpt-5 once streaming propagates
        """
        self.model = model
        self.client = OpenAI()

    def synthesize_drop(
        self,
        session_path: Path,
        drop_id: str,
        existing_latest: Optional[str] = None,
        mode: str = "general"
    ) -> str:
        """
        Synthesize a new drop into latest.md (iterative synthesis).

        Args:
            session_path: Path to session directory
            drop_id: Drop folder name (e.g., "drop-1")
            existing_latest: Existing latest.md content (for incremental update)
            mode: Research mode ("icp-validation", "gtm-execution", or "general")

        Returns:
            Updated latest.md content (markdown string)
            - ICP mode: ICP Hypothesis Document format
            - GTM mode: GTM Playbook Document format
            - General mode: Standard latest.md format
        """
        drop_path = session_path / "drops" / drop_id

        # Load drop artifacts
        researcher_outputs = self._load_researcher_outputs(drop_path)
        user_context = self._load_user_context(drop_path)

        # Load existing latest.md if it exists (compacted state)
        if existing_latest is None:
            latest_file = session_path / "latest.md"
            if latest_file.exists():
                existing_latest = latest_file.read_text(encoding="utf-8")

        # Synthesize using GPT-4o (iterative update, mode-aware)
        latest_md = self._synthesize_incremental(
            existing_latest=existing_latest,
            new_outputs=researcher_outputs,
            user_context=user_context,
            drop_id=drop_id,
            mode=mode
        )

        return latest_md

    def _load_researcher_outputs(self, drop_path: Path) -> List[Dict[str, str]]:
        """Load all researcher-*-output.md files from drop folder."""
        outputs = []

        for file in drop_path.glob("researcher-*-output.md"):
            findings = file.read_text(encoding="utf-8")
            researcher_id = file.stem  # e.g., "researcher-demo-output"

            outputs.append({
                "researcher_id": researcher_id,
                "findings": findings
            })

        return outputs

    def _load_user_context(self, drop_path: Path) -> Optional[str]:
        """Load user-context.md if it exists."""
        context_file = drop_path / "user-context.md"
        if context_file.exists():
            return context_file.read_text(encoding="utf-8")
        return None

    def _synthesize_incremental(
        self,
        existing_latest: Optional[str],
        new_outputs: List[Dict[str, str]],
        user_context: Optional[str],
        drop_id: str,
        mode: str = "general"
    ) -> str:
        """
        Synthesize new findings into existing latest.md (iterative update).

        Uses XML-structured prompt following Anthropic guidance.
        Mode-aware: generates ICP Hypothesis Document or general latest.md.
        """
        # Build context section
        context_parts = []

        if existing_latest:
            context_parts.append(f"<existing_latest>\n{existing_latest}\n</existing_latest>")

        if user_context:
            context_parts.append(f"<user_context>\n{user_context}\n</user_context>")

        context_parts.append("<new_findings>")
        for output in new_outputs:
            context_parts.append(f"### {output['researcher_id']}")
            context_parts.append(output['findings'])
            context_parts.append("")
        context_parts.append("</new_findings>")

        context = "\n".join(context_parts)

        # Build mode-specific instructions
        if mode == "icp-validation":
            task_description = "Update the ICP Hypothesis Document with new validation findings."
            structure_guidance = """
STRUCTURE (ICP Hypothesis Document):
First drop: Create new ICP Hypothesis Document with:
- Executive Summary (who is best customer, why, confidence level)
- Fit Scores (A/B/C/D tiers with observable criteria)
- Intent Signals (Clay-executable: first-party, third-party, environmental)
- Hypothesis Evolution (what changed from assumptions to evidence)
- Next Validation Steps

Subsequent drops: Update fit scores, add/refine signals, track hypothesis evolution
"""
            specific_principles = """
ICP-SPECIFIC PRINCIPLES:
- Observable signals only: ❌ "innovative companies" → ✅ "adopted GPT-4 API within 3 months of launch"
- Clay-executable: Every signal must be findable via Clay integrations
- Evidence-based fit scores: A/B/C/D based on conversion lift, LTV, retention data
- Invalidate assumptions: Track ~~Drop 1 assumed X~~ → Drop 2 evidence shows Y
"""
        elif mode == "gtm-execution":
            task_description = "Update the GTM Playbook Document with new execution findings."
            structure_guidance = """
STRUCTURE (GTM Playbook Document):
- Channel Validation (which channels work, evidence)
- Messaging Framework (what resonates, pain points)
- Execution Tactics (concrete playbooks)
- Success Metrics (KPIs, benchmarks)
"""
            specific_principles = """
GTM-SPECIFIC PRINCIPLES:
- Tactical focus: Concrete playbooks, not theory
- Metric-driven: Conversion rates, CAC, LTV for each channel/tactic
- Evidence-based: Customer quotes, A/B test results, cohort analysis
"""
        else:  # general mode
            task_description = "Update the living truth document (latest.md) with new research findings."
            structure_guidance = """
STRUCTURE:
First drop: Create new latest.md with:
- TL;DR (1-2 sentences)
- Key Insights (organized by theme)
- Strategic Implications
- Actions

Subsequent drops: Update existing sections, add new themes as needed
"""
            specific_principles = ""

        # Build instructions (following Anthropic's synthesis patterns + prompt engineering best practices)
        instructions = f"""
TASK: {task_description}

Research Mode: {mode}
Drop ID: {drop_id}
Date: {datetime.now().strftime('%Y-%m-%d')}

SYNTHESIS APPROACH (Chain of Thought):
Before writing, think through:
1. What are the key findings in the new research?
2. Do any findings contradict existing claims?
3. Where do new findings fit in the existing structure?
4. What confidence level should each claim have?

SYNTHESIS PRINCIPLES:
- Iterative update: Add to existing content, don't rewrite from scratch
- Detect contradictions: Apply strikethrough to invalidated claims
- Preserve strategic WHY: Keep user's decision context visible
- Concise output: Target 1500-2000 tokens

{specific_principles}

CONTRADICTION HANDLING:
When new findings contradict existing claims:
- Keep old claim with strikethrough: ~~The MLOps market was $1.2B in 2023~~
- Add new claim with source: The MLOps market is $2.2B in 2024 (Source: Drop {drop_id})
- Maintain transparency: Show evolution of understanding

{structure_guidance}

METADATA TO INCLUDE:
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
- Drop ID: {drop_id}
- Confidence levels: High/Medium/Low for key claims

EXAMPLE (Contradiction Handling):
```markdown
## Market Sizing
~~Global MLOps market valued at $1.2B in 2024 (Drop 1 - Medium confidence)~~

Updated: Global MLOps market valued at $2.2B in 2024 (Drop 2 - High confidence, Grand View Research)
- Previous estimate was based on limited sources
- New finding corroborated by 3 analyst reports
```

OUTPUT:
Return ONLY the updated latest.md content in markdown format.
Do NOT include explanations outside the document.
"""

        # Call GPT-4o for synthesis
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a research synthesis agent. Your job is to create concise, actionable intelligence briefs from research findings."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\n{instructions}"
                }
            ],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=3000  # Allow room for synthesis
        )

        latest_md = response.choices[0].message.content
        return latest_md

    def save_latest(self, session_path: Path, content: str):
        """Save latest.md to session directory."""
        latest_file = session_path / "latest.md"
        latest_file.write_text(content, encoding="utf-8")
