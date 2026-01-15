"""Schema models for generic content extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GenericContent(BaseModel):
    """LLM-generated generic content (fallback for unstructured content)."""

    content_type: Literal["generic"]
    topic: str = Field(..., description="Clinical topic or subject")
    section_type: str = Field(
        ...,
        description="Type of content (e.g., background, epidemiology, definitions, glossary)",
    )
    summary: str = Field(
        ..., description="Brief summary of the content in 1-2 sentences"
    )
    key_points: list[str] = Field(
        default_factory=list, description="Main takeaways or important facts"
    )
    raw_text: str = Field(
        default="",
        description="Preserved original text for later schema refinement or analysis",
    )
