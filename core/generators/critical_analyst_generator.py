"""
Critical Analyst Generator - Pokes holes in research to counterbalance AI agreeableness.

Analyzes researcher outputs directly (NOT synthesis) to:
- Challenge assumptions and identify logical gaps
- Flag weak evidence or cherry-picked data
- Highlight unstated assumptions
- Identify critical unanswered questions

Runs AFTER each research drop (peer to synthesis, not downstream).
Provides HQ with critical context to facilitate better user conversations.

This "shows the user where the gold is" - pointing to gaps that need investigation.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class CriticalAnalystGenerator:
    """
    Generates critical-analysis.md by analyzing researcher outputs.

    Runs AFTER each research drop (peer to synthesis):
    - Analyzes raw researcher outputs for gaps and weaknesses
    - Pokes holes in research (counterbalances AI agreeableness)
    - Identifies critical unanswered questions
    - Provides HQ with context to guide next user conversation

    Example:
        generator = CriticalAnalystGenerator()
        analysis = generator.analyze_drop(
            session_path=Path("projects/demo-company/sessions/session-1"),
            drop_id="drop-1"
        )
    """

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize Critical Analyst Generator.

        Args:
            model: OpenAI model for analysis (default: gpt-4o)
                   TODO: Switch to gpt-5 once streaming propagates
        """
        self.model = model
        self.client = OpenAI()

    def analyze_drop(
        self,
        session_path: Path,
        drop_id: str
    ) -> str:
        """
        Generate critical analysis of research drop.

        Analyzes researcher outputs directly (NOT synthesis).

        Args:
            session_path: Path to session directory
            drop_id: Drop folder name (e.g., "drop-1")

        Returns:
            Critical analysis markdown content
        """
        drop_path = session_path / "drops" / drop_id

        # Load user context to understand strategic WHY (the gold)
        user_context = self._load_user_context(drop_path)

        # Load researcher outputs - THIS is what we analyze
        researcher_outputs = self._load_researcher_outputs(drop_path)

        if not researcher_outputs:
            raise ValueError(f"No researcher outputs found in {drop_path}")

        # Generate critical analysis
        analysis = self._generate_analysis(
            user_context=user_context,
            researcher_outputs=researcher_outputs,
            drop_id=drop_id
        )

        return analysis

    def _load_user_context(self, drop_path: Path) -> Optional[str]:
        """Load user-context.md if it exists."""
        context_file = drop_path / "user-context.md"
        if context_file.exists():
            return context_file.read_text(encoding="utf-8")
        return None

    def _load_researcher_outputs(self, drop_path: Path) -> list[dict]:
        """Load all researcher outputs for critical analysis."""
        outputs = []
        for file in drop_path.glob("researcher-*-output.md"):
            outputs.append({
                "researcher_id": file.stem,
                "content": file.read_text(encoding="utf-8")
            })
        return outputs

    def _generate_analysis(
        self,
        user_context: Optional[str],
        researcher_outputs: list[dict],
        drop_id: str
    ) -> str:
        """
        Generate critical analysis using GPT-4o.

        Analyzes researcher outputs directly (NOT synthesis).
        Follows /prompts/critical-analyst.md framework.
        """
        # Build context section
        context_parts = []

        if user_context:
            context_parts.extend([
                "<user_context>",
                "This is the GOLD - the strategic WHY that matters.",
                user_context,
                "</user_context>",
                ""
            ])

        context_parts.append("<researcher_outputs>")
        context_parts.append(f"Total researchers: {len(researcher_outputs)}")
        context_parts.append("")

        for output in researcher_outputs:
            context_parts.append(f"### {output['researcher_id']}")
            context_parts.append(output['content'])
            context_parts.append("")

        context_parts.append("</researcher_outputs>")

        context = "\n".join(context_parts)

        # Load critical analyst prompt framework
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "critical-analyst.md"
        if prompt_file.exists():
            analyst_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            # Fallback if prompt file not found
            analyst_prompt = self._get_default_analyst_prompt()

        # Build instructions (following Anthropic prompt engineering best practices)
        instructions = f"""
TASK: Critically analyze researcher outputs to identify gaps and weaknesses.

Drop ID: {drop_id}
Date: {datetime.now().strftime('%Y-%m-%d')}

CRITICAL THINKING APPROACH (Chain of Thought):
Before writing, think through:
1. Evidence Quality: Are sources credible? Is data cherry-picked?
2. Logic: Do conclusions follow from evidence? Any unstated assumptions?
3. Completeness: What perspectives are missing? What questions remain unanswered?
4. Relevance to Gold: Which gaps matter most for the user's strategic WHY?

YOUR ROLE:
AI has a tendency to be agreeable. You are the counterbalance.
Analyze with skepticism and rigor, not to dismiss work, but to strengthen it.

ANALYSIS FRAMEWORK (from /prompts/critical-analyst.md):
{analyst_prompt}

WHAT TO FLAG:
- Weak evidence: Cherry-picked data, outdated sources, weak citations
- Logical gaps: Conclusions that don't follow, correlation mistaken for causation
- Unstated assumptions: Hidden beliefs that could be wrong
- Missing perspectives: Viewpoints not considered
- Unanswered questions: Critical gaps relevant to user's strategic WHY

CRITICAL GUIDANCE:
- Be constructive: Identify problems AND suggest how to fix them
- Focus on gaps that matter for the user's decision context (the "gold")
- Suggest specific follow-on research areas
- Separate minor issues from critical flaws

EXAMPLE (Strong Critical Analysis):
```markdown
## Critical Concerns

### Major Issue: Market Size Lacks Verification
**Problem**: Only one source cited for $2.2B market size (Grand View Research)
- **Impact**: Decision based on single analyst report could be risky
- **Evidence**: No corroboration from Gartner, Forrester, or IDC
- **Recommendation**: Next drop should verify with 2-3 additional analyst sources

## Unanswered Questions
1. What's the TAM breakdown by industry vertical? (Critical for targeting)
2. How does competitor X achieve their claimed ROI? (Missing validation)
3. What hidden costs exist beyond platform fees? (Affects TCO analysis)

## Recommended Next Steps
- Research Drop 2: Focus on market size verification + vertical breakdown
- Validate competitor claims with case studies or independent reviews
```

OUTPUT:
Return ONLY the critical-analysis.md content (markdown).
Follow the framework structure above.
Include all required sections from the framework.
"""

        # Call GPT-4o for analysis
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a critical analyst evaluating research quality and identifying gaps. Your role is to strengthen research by finding weaknesses and suggesting improvements."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\n{instructions}"
                }
            ],
            temperature=0.4,  # Slightly higher for creative gap identification
            max_tokens=3000  # Allow room for thorough analysis
        )

        analysis = response.choices[0].message.content
        return analysis

    def _get_default_analyst_prompt(self) -> str:
        """Fallback analyst framework if prompt file not found."""
        return """
## Analysis Framework

### Evidence Quality Check
- Are sources credible and current?
- Is sampling adequate or cherry-picked?
- Are outliers or contradictory data addressed?

### Logic Evaluation
- Do conclusions logically follow from evidence?
- Are there unstated assumptions?
- Is correlation mistaken for causation?

### Completeness Assessment
- What perspectives are missing?
- Are known limitations acknowledged?
- Does the scope match the claims made?

### Output Format
# Critical Analysis: [Research Topic]

## Strengths
[What the research does well]

## Critical Concerns
### Major Issues
[Problems that could affect decisions]

### Minor Issues
[Smaller concerns]

## Unanswered Questions
[Critical gaps for follow-on research]

## Recommended Next Steps
[Specific areas to investigate in next drop]
"""

    def save_analysis(self, drop_path: Path, content: str):
        """Save critical-analysis.md to drop directory."""
        analysis_file = drop_path / "critical-analysis.md"
        analysis_file.write_text(content, encoding="utf-8")
