"""Schema models for warning signs / red flags extraction."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class NumericTrigger(BaseModel):
    """Numeric threshold that triggers emergency response."""

    parameter: str = Field(..., description="What is being measured")
    threshold_value: float = Field(..., description="The threshold value")
    operator: Literal["<", "≤", ">", "≥", "="] = Field(..., description="Comparison operator")
    unit: str = Field(..., description="Unit of measurement")


class WarningSigns(BaseModel):
    """Red flags and danger signs that require immediate attention.
    
    Use for: Emergency triage boxes, danger sign lists, urgent referral triggers.
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
    priority_score: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Urgency priority (1=routine, 10=life-threatening). Red boxes = 10.",
    )
    triggers: list[str] = Field(
        ..., description="Clinical signs that activate emergency response"
    )
    trigger_thresholds: list[NumericTrigger] = Field(
        default_factory=list,
        description="Machine-readable numeric thresholds (e.g., Temp > 40°C, BP < 90/60)",
    )
    immediate_steps: list[str] = Field(
        ..., description="Ordered list of medical actions to perform immediately"
    )
    safety_checks: list[str] = Field(
        default_factory=list,
        description="Specific warnings and contraindications",
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
