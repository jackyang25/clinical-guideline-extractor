"""Automatic guideline metadata extraction from cover page."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from extraction.llm.client import AnthropicVisionClient
from extraction.llm.parsers import strip_json_fence
from extraction.processors.pdf import PageImage
from schemas.metadata_extraction.models import GuidelineMetadataExtraction


async def extract_metadata_async(
    first_page: PageImage, client: AnthropicVisionClient
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
