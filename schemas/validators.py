"""Unified validation for all content types using discriminated union."""

from __future__ import annotations

from typing import Union

from pydantic import ValidationError

from schemas.clinical_pathways.models import ClinicalPathway
from schemas.diagnostic_criteria.models import DiagnosticCriteria
from schemas.drug_monographs.models import DrugMonograph
from schemas.generic.models import GenericContent
from schemas.patient_education.models import PatientEducation
from schemas.reference_tables.models import ReferenceTable
from schemas.warning_signs.models import WarningSigns

# Discriminated union of all content types
ClinicalContent = Union[
    ClinicalPathway,
    DiagnosticCriteria,
    DrugMonograph,
    GenericContent,
    PatientEducation,
    ReferenceTable,
    WarningSigns,
]


def sanitize_payload(payload: dict) -> dict:
    """Remove system-managed fields that model should not set."""
    
    # fields that are system/human-controlled only
    protected_fields = {"human_audit", "audit", "chunk_info"}
    
    # create a copy and remove protected fields
    sanitized = {k: v for k, v in payload.items() if k not in protected_fields}
    
    return sanitized


def validate_content(
    payloads: list[dict],
) -> tuple[list[ClinicalContent], list[str]]:
    """Validate content payloads using discriminated union.
    
    Each payload must have a 'content_type' field that determines which schema to use.
    """

    valid: list[ClinicalContent] = []
    errors: list[str] = []

    for index, item in enumerate(payloads):
        # strip any audit fields model may have included
        sanitized = sanitize_payload(item)
        
        # get content type for error messages
        content_type = sanitized.get("content_type", "unknown")
        
        try:
            # Pydantic automatically dispatches to correct model based on content_type
            validated = None
            if content_type == "clinical_pathway":
                validated = ClinicalPathway.model_validate(sanitized)
            elif content_type == "reference_table":
                validated = ReferenceTable.model_validate(sanitized)
            elif content_type == "drug_monograph":
                validated = DrugMonograph.model_validate(sanitized)
            elif content_type == "warning_signs":
                validated = WarningSigns.model_validate(sanitized)
            elif content_type == "diagnostic_criteria":
                validated = DiagnosticCriteria.model_validate(sanitized)
            elif content_type == "patient_education":
                validated = PatientEducation.model_validate(sanitized)
            elif content_type == "generic":
                validated = GenericContent.model_validate(sanitized)
            else:
                errors.append(
                    f"Item {index}: Unknown content_type '{content_type}'. "
                    f"Must be one of: clinical_pathway, reference_table, drug_monograph, "
                    f"warning_signs, diagnostic_criteria, patient_education, generic"
                )
                continue
            
            valid.append(validated)
        except ValidationError as exc:
            errors.append(f"Item {index} (type: {content_type}): {exc}")

    return valid, errors
