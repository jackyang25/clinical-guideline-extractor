"""Schema models for patient education content extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RedFlag(BaseModel):
    """Structured red flag trigger for patient alerting."""

    symptom: str = Field(..., description="The warning symptom or sign")
    action: str = Field(..., description="What patient should do (e.g., 'Call doctor immediately', 'Go to ER')")
    timeframe: str = Field(default="", description="How quickly to act")


class PatientEducation(BaseModel):
    """Patient and caregiver education content.
    
    Use for: Home care instructions, prevention messages, when to return guidance.
    Not for: Clinical protocols (use clinical_pathway), warning signs (use warning_signs).
    """

    content_type: Literal["patient_education"]
    topic: str = Field(..., description="Clinical topic")
    target_audience: Literal["patient", "caregiver", "both"] = Field(
        ..., description="Who this education is for"
    )
    education_type: Literal[
        "prevention",
        "self_care",
        "when_to_return",
        "medication_instructions",
        "lifestyle",
        "general_information",
    ] = Field(..., description="Type of education content")
    key_messages: list[str] = Field(
        default_factory=list,
        description="Main education points to communicate",
    )
    instructions: list[str] = Field(
        default_factory=list,
        description="Step-by-step instructions if applicable",
    )
    red_flags: list[RedFlag] = Field(
        default_factory=list,
        description="Structured 'call doctor if...' triggers for patient alerts",
    )
    when_to_seek_care: list[str] = Field(
        default_factory=list,
        description="Symptoms or situations requiring return to clinic (legacy field, prefer red_flags)",
    )
    things_to_avoid: list[str] = Field(
        default_factory=list,
        description="Actions or substances to avoid",
    )
    follow_up: str = Field(
        default="", description="Follow-up instructions if specified"
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹')",
    )
