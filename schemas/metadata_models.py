"""System-managed metadata and audit models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HumanAudit(BaseModel):
    """Human/system-controlled audit metadata (same structure at all levels)."""

    status: Literal["draft", "pending_review", "approved", "rejected"] = Field(
        default="draft"
    )
    version: int = Field(default=1, description="Version number")
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When this item was created",
    )
    created_by: str = Field(default="system", description="User who created this item")
    reviewed_by: str = Field(default="", description="Person who reviewed this item")
    approval_date: str = Field(default="", description="When this item was approved")
    notes: str = Field(default="", description="Reviewer comments or notes")


class GuidelineInfo(BaseModel):
    """Guideline-level information (system-provided, not LLM)."""

    guideline_id: str
    guideline_name: str
    guideline_version: str = Field(default="")
    country: str = Field(default="", description="Country of jurisdiction")
    jurisdiction: str = Field(
        default="", description="Specific jurisdiction (e.g., National, Provincial)"
    )
    organization: str = Field(
        default="", description="Publishing organization or authority"
    )
    regulatory_status: Literal["official", "draft", "guidance", "archived"] = Field(
        default="draft"
    )


class PageInfo(BaseModel):
    """Page-level information (system-provided, not LLM)."""

    page_number: int
    extraction_date: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When page was extracted",
    )
    extraction_status: Literal["success", "validation_failed", "error"] = Field(
        default="success",
        description="Status of page extraction",
    )
    needs_retry: bool = Field(
        default=False,
        description="Whether this page needs to be re-extracted",
    )


class ChunkInfo(BaseModel):
    """Chunk-level information (system-provided, not LLM).
    
    Minimal in hierarchical structure since parent context is in guideline_info/page_info.
    """

    chunk_id: str = Field(..., description="Unique identifier for this chunk")
