"""Automatic guideline metadata extraction from cover page."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from extraction.llm.client import VisionClient
from extraction.llm.parsers import strip_json_fence
from extraction.processors.pdf import PageImage
from schemas.metadata_extraction.models import GuidelineMetadataExtraction
from schemas.metadata_models import GuidelineInfo


async def extract_metadata_async(
    first_page: PageImage, client: VisionClient
) -> GuidelineMetadataExtraction:
    """Extract guideline metadata from the first page."""
    
    # load prompt from YAML
    prompt_path = Path(__file__).resolve().parent.parent / "schemas" / "guideline_metadata_prompt.yaml"
    from extraction.llm.parsers import load_prompt
    prompt = load_prompt(prompt_path)
    
    # call LLM
    raw_text, _ = await client.extract(prompt, first_page.image_bytes, first_page.mime_type)
    
    # parse JSON
    cleaned = strip_json_fence(raw_text)
    payload = json.loads(cleaned)
    
    # validate and return
    return GuidelineMetadataExtraction.model_validate(payload)


def extract_metadata(
    first_page: PageImage, client: AnthropicVisionClient
) -> GuidelineMetadataExtraction:
    """Synchronous wrapper for metadata extraction."""
    return asyncio.run(extract_metadata_async(first_page, client))


def metadata_to_guideline_info(
    metadata: GuidelineMetadataExtraction,
    regulatory_status: str = "draft"
) -> GuidelineInfo:
    """Transform extracted metadata into GuidelineInfo.
    
    Combines jurisdiction_level and jurisdiction_name into single field,
    generates guideline_id if not present, and maps to output structure.
    """
    # combine jurisdiction fields if both present
    if metadata.jurisdiction_level and metadata.jurisdiction_name:
        jurisdiction = f"{metadata.jurisdiction_level} - {metadata.jurisdiction_name}"
    else:
        jurisdiction = metadata.jurisdiction_level or metadata.jurisdiction_name
    
    # use extracted id or generate from name
    guideline_id = metadata.guideline_id or metadata.guideline_name.lower().replace(" ", "_")[:50]
    
    return GuidelineInfo(
        guideline_id=guideline_id,
        guideline_name=metadata.guideline_name,
        guideline_version=metadata.guideline_version,
        country=metadata.country,
        jurisdiction=jurisdiction,
        organization=metadata.organization,
        regulatory_status=regulatory_status,
    )
