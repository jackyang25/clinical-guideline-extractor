"""Output formatting for hierarchical structure."""

from __future__ import annotations

from typing import Any

from schemas.metadata_models import GuidelineInfo, HumanAudit, PageInfo


def wrap_page_output(
    page_number: int,
    chunks: list[dict[str, Any]],
    extracted_by: str,
    extraction_status: str = "success",
    needs_retry: bool = False,
) -> dict[str, Any]:
    """Wrap chunks with page-level information and audit."""
    page_info = PageInfo(
        page_number=page_number,
        extraction_status=extraction_status,
        needs_retry=needs_retry,
    )
    page_audit = HumanAudit(created_by=extracted_by)
    
    return {
        "page_info": page_info.model_dump(),
        "human_audit": page_audit.model_dump(),
        "llm_chunks": chunks,
    }


def wrap_guideline_output(
    guideline_info: GuidelineInfo,
    guideline_audit: HumanAudit,
    pages: list[dict[str, Any]],
) -> dict[str, Any]:
    """Wrap all pages with guideline-level information and audit."""
    
    return {
        "guideline_info": guideline_info.model_dump(),
        "human_audit": guideline_audit.model_dump(),
        "pages": pages,
        "total_pages": len(pages),
        "total_chunks": sum(len(p["llm_chunks"]) for p in pages),
    }
