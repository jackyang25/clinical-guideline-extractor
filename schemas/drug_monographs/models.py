"""Schema models for drug monograph extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DosingRegimen(BaseModel):
    """Dosing information for a specific route and indication."""

    route: str = Field(..., description="Administration route (e.g., oral, IV)")
    dose: str = Field(..., description="Dose with units (e.g., 500mg, 10mg/kg)")
    frequency: str = Field(..., description="How often (e.g., twice daily, every 8h)")
    duration: str = Field(
        default="", description="How long to continue (e.g., 7 days, until resolved)"
    )
    special_populations: str = Field(
        default="", description="Adjustments for renal/hepatic impairment, elderly, etc"
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
    notes: list[str] = Field(
        default_factory=list, description="Important clinical pearls or warnings"
    )
