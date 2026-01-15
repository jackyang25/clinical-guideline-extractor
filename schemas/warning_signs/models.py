"""Schema models for warning signs / red flags extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WarningSigns(BaseModel):
    """Red flags and danger signs that require immediate attention.
    
    Use for: Emergency triage boxes, danger sign lists, "when to seek care" sections.
    Not for: IF/THEN protocols (use clinical_pathway instead).
    """

    content_type: Literal["warning_signs"]
    topic: str = Field(..., description="Clinical topic or condition")
    condition_context: str = Field(
        default="", description="The condition these warning signs relate to"
    )
    urgency: Literal["emergency", "urgent"] = Field(
        ..., description="How urgent is the response needed"
    )
    signs_symptoms: list[str] = Field(
        default_factory=list,
        description="List of warning signs or symptoms to watch for",
    )
    immediate_actions: list[str] = Field(
        default_factory=list,
        description="What to do immediately if signs present",
    )
    referral_required: bool = Field(
        default=True, description="Whether referral is required when signs present"
    )
    referral_destination: str = Field(
        default="", description="Where to refer (e.g., hospital, specialist)"
    )
    timeframe: str = Field(
        default="", description="How quickly action is needed (e.g., 'within 1 hour')"
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹')",
    )
