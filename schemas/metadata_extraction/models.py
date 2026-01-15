"""Schema for extracting guideline metadata from cover page."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GuidelineMetadataExtraction(BaseModel):
    """Metadata extracted from guideline cover page."""

    guideline_name: str = Field(
        ..., description="Full title of the guideline document"
    )
    guideline_id: str = Field(
        default="",
        description="Explicit identifier if present (document number, reference code, ISBN, etc.)",
    )
    guideline_version: str = Field(
        default="", description="Version, edition number if visible"
    )
    publication_date: str = Field(
        default="", description="Publication or original release date"
    )
    last_updated_date: str = Field(
        default="", description="Last revised/updated date if different from publication"
    )
    organization: str = Field(
        default="", description="Publishing organization or department"
    )
    country: str = Field(default="", description="Country where guideline applies")
    jurisdiction_level: str = Field(
        default="", description="Scope level: National, Provincial, Regional, State, etc."
    )
    jurisdiction_name: str = Field(
        default="", description="Specific jurisdiction name if stated (e.g., Western Cape, Gauteng)"
    )
    language: str = Field(
        default="", description="Language of the document if explicitly stated"
    )
    intended_audience: str = Field(
        default="",
        description="Target audience if explicitly stated (e.g., Primary care clinicians, CHWs)",
    )
