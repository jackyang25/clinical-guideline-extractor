"""Validation for clinical pathway extraction."""

from __future__ import annotations

from pydantic import ValidationError

from schemas.clinical_pathways.models import ClinicalGuideline


def sanitize_payload(payload: dict) -> dict:
    """Remove system-managed fields that model should not set."""
    
    # fields that are system/human-controlled only
    protected_fields = {"human_audit", "audit", "chunk_info"}
    
    # create a copy and remove protected fields
    sanitized = {k: v for k, v in payload.items() if k not in protected_fields}
    
    return sanitized


def validate_guidelines(
    payloads: list[dict],
) -> tuple[list[ClinicalGuideline], list[str]]:
    """Validate guideline payloads using the schema."""

    valid: list[ClinicalGuideline] = []
    errors: list[str] = []

    for index, item in enumerate(payloads):
        # strip any audit fields model may have included
        sanitized = sanitize_payload(item)
        
        try:
            valid.append(ClinicalGuideline.model_validate(sanitized))
        except ValidationError as exc:
            errors.append(f"Item {index}: {exc}")

    return valid, errors
