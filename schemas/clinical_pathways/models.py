"""Schema models for clinical guideline extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ClinicalCriteria(BaseModel):
    """Clinical criteria for a pathway."""

    conditions: list[str] = Field(default_factory=list)
    emergency_triggers: list[str] = Field(default_factory=list)


class Protocol(BaseModel):
    """Protocol actions for a pathway."""

    assess: list[str] = Field(default_factory=list)
    treat: list[str] = Field(default_factory=list)
    advise: list[str] = Field(default_factory=list)


class LogicConnection(BaseModel):
    """Link to another section or page."""

    trigger: str
    target: str
    type: Literal[
        "escalation",
        "comorbidity",
        "differential_diagnosis",
        "follow_up",
        "alternate_pathway",
        "prerequisite",
    ]


class ClinicalPathway(BaseModel):
    """LLM-generated clinical pathway content (pure extraction, no system metadata)."""

    content_type: Literal["clinical_pathway"]
    pathway_type: Literal[
        "diagnostic",
        "treatment",
        "triage",
        "screening",
        "monitoring",
        "mixed",
    ] = Field(..., description="Primary purpose of this pathway")
    topic: str = Field(..., description="Clinical topic or subject")
    specific_scenario: str
    visual_structure: Literal[
        "flowchart_path",
        "routine_care_table",
        "emergency_box",
        "general_info",
    ]
    urgency: Literal["emergency", "urgent", "routine"]
    prescriber_level: Literal[
        "nurse",
        "doctor",
        "specialist",
        "patient_self_care",
        "not_applicable",
    ]
    clinical_criteria: ClinicalCriteria
    protocol: Protocol
    logic_connections: list[LogicConnection] = Field(default_factory=list)
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹', '→ TB')",
    )
    disposition: str
