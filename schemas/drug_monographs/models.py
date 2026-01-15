"""Schema models for drug monograph extraction."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class DosageLogic(BaseModel):
    """Structured dosage with machine-readable components."""

    value: float = Field(..., description="Numeric dose amount")
    unit: str = Field(..., description="Dose unit (e.g., mg, mg/kg, mL)")
    max_single_dose: Optional[float] = Field(
        default=None, description="Maximum single dose (same unit as value)"
    )
    max_daily_dose: Optional[float] = Field(
        default=None, description="Maximum daily dose (same unit as value)"
    )


class DosingRegimen(BaseModel):
    """Dosing information for a specific route and indication."""

    route: str = Field(..., description="Administration route (e.g., oral, IV, IM)")
    dose: str = Field(..., description="Human-readable dose (e.g., 500mg, 10mg/kg)")
    dosage_logic: Optional[DosageLogic] = Field(
        default=None, description="Machine-readable structured dosage for computation"
    )
    frequency: str = Field(..., description="How often (e.g., twice daily, every 8h)")
    duration: str = Field(
        default="", description="How long to continue (e.g., 7 days, until resolved)"
    )
    special_populations: str = Field(
        default="", description="Adjustments for renal/hepatic impairment, elderly, etc"
    )
    administration_instructions: list[str] = Field(
        default_factory=list,
        description="Step-by-step prep/admin instructions (e.g., 'Slow IV push over 5 min', 'Dilute with saline')",
    )


class DrugMonograph(BaseModel):
    """LLM-generated drug monograph content (pure extraction, no system metadata)."""

    content_type: Literal["drug_monograph"]
    topic: str = Field(..., description="Clinical topic or subject")
    drug_name: str = Field(..., description="Generic drug name")
    brand_names: list[str] = Field(
        default_factory=list, description="Common brand/trade names"
    )
    drug_class: str = Field(
        default="", description="Pharmacological class (e.g., ACE inhibitor)"
    )
    indications: list[str] = Field(
        default_factory=list, description="Approved uses and indications"
    )
    contraindications: list[str] = Field(
        default_factory=list, description="Absolute contraindications"
    )
    dosing: list[DosingRegimen] = Field(
        default_factory=list, description="Dosing regimens"
    )
    adverse_effects: list[str] = Field(
        default_factory=list, description="Common and serious adverse effects"
    )
    drug_interactions: list[str] = Field(
        default_factory=list, description="Significant drug-drug interactions"
    )
    monitoring: list[str] = Field(
        default_factory=list,
        description="Required monitoring (labs, vitals, symptoms)",
    )
    pregnancy_category: str = Field(
        default="", description="Pregnancy safety category or recommendation"
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹')",
    )
    notes: list[str] = Field(
        default_factory=list, description="Important clinical pearls or warnings"
    )
