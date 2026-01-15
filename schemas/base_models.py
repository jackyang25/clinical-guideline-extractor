"""Base models shared across all extraction schemas.

This module re-exports models from specialized modules for backward compatibility.
"""

from schemas.metadata_models import ChunkInfo, Footnote, GuidelineInfo, HumanAudit, PageInfo

__all__ = [
    "HumanAudit",
    "GuidelineInfo",
    "PageInfo",
    "ChunkInfo",
    "Footnote",
]
