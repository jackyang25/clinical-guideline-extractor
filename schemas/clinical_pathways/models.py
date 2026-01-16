"""Schema models for clinical guideline extraction."""

from __future__ import annotations

from typing import Literal, Optional

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


class NumericRange(BaseModel):
    """Numeric range with explicit boundaries for clinical thresholds."""

    parameter: str = Field(..., description="What is being measured (e.g., 'glucose', 'BP systolic')")
    min_value: Optional[float] = Field(default=None, description="Minimum value (null if unbounded below)")
    max_value: Optional[float] = Field(default=None, description="Maximum value (null if unbounded above)")
    inclusive_min: bool = Field(default=True, description="Whether min is inclusive (≥ vs >)")
    inclusive_max: bool = Field(default=True, description="Whether max is inclusive (≤ vs <)")
    unit: str = Field(..., description="Unit of measurement (e.g., 'mmol/L', 'mmHg')")


class PathwayLogic(BaseModel):
    """Structured if/then logic for clinical decision-making.
    
    CRITICAL Rules:
    - Capture BOTH positive and negative branches
    - Use compound AND conditions for nested gates (e.g., 'Glucose ≥ 11.1 AND Ketones present')
    - Each distinct path through nested logic should be a separate entry
    - If a branch leads to 'no action', use then_action: 'Routine care' or 'Exit pathway'
    
    Example of nested conditional (ketone gate):
    - Entry 1: if_condition="Glucose ≥ 11.1 AND Ketones present", then_action="Give IV fluids"
    - Entry 2: if_condition="Glucose ≥ 11.1 AND Ketones absent", then_action="Routine monitoring"
    """

    if_condition: str = Field(
        ..., 
        description=(
            "The clinical condition or patient state that triggers this action. "
            "Use compound AND conditions to capture nested decision gates "
            "(e.g., 'Glucose ≥ 11.1 AND Symptoms present AND Ketones present')"
        )
    )
    then_action: str = Field(
        ..., 
        description=(
            "The specific medical action or intervention to take. "
            "Use 'Routine care' or 'Exit pathway' for negative branches. "
            "For time-staged treatments, reference implementation_notes for detailed staging."
        )
    )
    next_step: str = Field(
        default="", 
        description="What happens next (e.g., recheck in 15 min, refer to page 16, monitor until ketones clear)"
    )


class ExitPoint(BaseModel):
    """Navigation point to another section, page, or escalation path."""

    condition: str = Field(
        ..., description="The trigger condition that activates this exit"
    )
    target: str = Field(
        ..., description="Where to go (e.g., 'page 16', 'Hospital referral', 'ICU')"
    )


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
    specific_scenario: str = Field(
        ..., 
        description="The specific patient situation. If global exclusions exist on page (e.g., 'Not for pregnant women'), append them here."
    )
    range_metadata: list[NumericRange] = Field(
        default_factory=list,
        description="Explicit numeric ranges with boundaries for machine filtering (e.g., glucose thresholds)",
    )
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
    pathway_logic: list[PathwayLogic] = Field(
        default_factory=list,
        description="Structured if/then decision logic for clinical reasoning (v3.0 enhancement)",
    )
    implementation_notes: list[str] = Field(
        default_factory=list,
        description=(
            "Step-by-step how-to instructions, including:\n"
            "- Injected footnote details (e.g., 'Footnote 1: Mix 15g sugar in 200mL water')\n"
            "- Drug preparation and dosing calculations\n"
            "- Temporal staging for time-dependent protocols (e.g., 'Stage 1 (First hour): 20mL/kg IV', 'Stage 2: 10mL/kg/hr')\n"
            "- Monitoring intervals with temporal context"
        ),
    )
    exit_points: list[ExitPoint] = Field(
        default_factory=list,
        description="Navigation points where patient care escalates or transitions to another pathway",
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹', '→ TB')",
    )
    disposition: str
