"""Schema models for diagnostic criteria / case definitions extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ClinicalFeatures(BaseModel):
    """Clinical features categorized by importance."""

    required: list[str] = Field(
        default_factory=list, description="Features that must be present"
    )
    suggestive: list[str] = Field(
        default_factory=list, description="Features that support the diagnosis"
    )
    excluding: list[str] = Field(
        default_factory=list, description="Features that rule out the diagnosis"
    )


class DiagnosticCriteria(BaseModel):
    """Case definitions and diagnostic criteria for conditions.
    
    Use for: Syndromic definitions, case criteria, diagnostic algorithms.
    Not for: Treatment protocols (use clinical_pathway), reference ranges (use reference_table).
    """

    content_type: Literal["diagnostic_criteria"]
    topic: str = Field(..., description="Clinical topic")
    condition_name: str = Field(..., description="Name of the condition being defined")
    definition_summary: str = Field(
        default="", description="Brief one-line definition if provided"
    )
    inclusion_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria that must be met for diagnosis",
    )
    exclusion_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria that rule out the diagnosis",
    )
    clinical_features: ClinicalFeatures = Field(
        default_factory=ClinicalFeatures,
        description="Clinical signs and symptoms categorized by importance",
    )
    differential_diagnoses: list[str] = Field(
        default_factory=list,
        description="Other conditions to consider",
    )
    diagnostic_tests: list[str] = Field(
        default_factory=list,
        description="Tests that confirm or support the diagnosis",
    )
    severity_classification: list[str] = Field(
        default_factory=list,
        description="Severity levels if defined (e.g., mild, moderate, severe)",
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹')",
    )
