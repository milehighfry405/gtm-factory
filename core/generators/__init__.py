"""
Generators module for synthesizing research outputs into living truth documents.

Follows Anthropic's context engineering patterns:
- Iterative synthesis (not single-shot)
- Token-efficient compaction
- Progressive disclosure via metadata

Post-drop generators (run after each research drop):
- LatestGenerator: Synthesize findings into latest.md
- CriticalAnalystGenerator: Poke holes in research (counterbalance AI agreeableness)
- SessionMetadataGenerator: Create metadata for progressive disclosure
"""

from core.generators.latest_generator import LatestGenerator
from core.generators.session_metadata_generator import SessionMetadataGenerator
from core.generators.critical_analyst_generator import CriticalAnalystGenerator

__all__ = ["LatestGenerator", "SessionMetadataGenerator", "CriticalAnalystGenerator"]
