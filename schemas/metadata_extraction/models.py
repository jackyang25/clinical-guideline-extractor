"""Schema for extracting guideline metadata from cover page."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GuidelineMetadataExtraction(BaseModel):
    """Metadata extracted from guideline cover page."""

    guideline_name: str = Field(
        ..., description="Full title of the guideline document"
    )
    guideline_version: str = Field(
        default="", description="Version, edition, or publication year"
    )
    organization: str = Field(
        default="", description="Publishing organization or department"
    )
    country: str = Field(default="", description="Country of origin")
    jurisdiction: str = Field(
        default="", description="Scope: National, Provincial, Regional, etc."
    )
