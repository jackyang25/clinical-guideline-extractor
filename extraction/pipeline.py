"""End-to-end pipeline for vision extraction."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from extraction.llm.client import AnthropicVisionClient
from extraction.llm.parsers import (
    ExtractionError,
    build_prompt,
    load_prompt,
    parse_json_response,
)
from extraction.processors.pdf import PageImage, render_pdf_bytes
from extraction.utils import ensure_dir, write_json, write_text
from schemas.validators import validate_content
from schemas.metadata_models import ChunkInfo, HumanAudit


@dataclass(frozen=True)
class PageOutput:
    """Container for per-page results."""

    page_number: int
    raw_text: str
    parsed_items: list[dict]
    validation_errors: list[str]
    usage: dict


async def _process_page(
    page: PageImage,
    base_prompt: str,
    guideline_id: str,
    guideline_name: str,
    guideline_version: str,
    output_dir: Path,
    client: AnthropicVisionClient,
    extracted_by: str,
    completion_callback: Callable[[int], None] | None = None,
) -> PageOutput:
    """Process a single page asynchronously."""
    prompt = build_prompt(
        base_prompt, guideline_id, guideline_name, guideline_version, page.page_number
    )
    raw_text, usage = await client.extract(prompt, page.image_bytes, page.mime_type)

    try:
        parsed_items = parse_json_response(raw_text)
    except ExtractionError:
        parsed_items = []

    # validate and get sanitized items (audit fields stripped)
    validated_items, validation_errors = validate_content(parsed_items)
    
    # all-or-nothing: if ANY chunk fails validation, discard entire page
    if validation_errors:
        # save raw output and errors for debugging
        raw_path = output_dir / f"page_{page.page_number:03d}_raw.txt"
        write_text(raw_path, raw_text)
        
        errors_path = output_dir / f"page_{page.page_number:03d}_errors.txt"
        write_text(errors_path, "\n".join(validation_errors))
        
        # return empty result with validation failure flag
        output = PageOutput(
            page_number=page.page_number,
            raw_text=raw_text,
            parsed_items=[],  # no chunks saved
            validation_errors=validation_errors,
            usage=usage,
        )
    else:
        # all chunks valid - convert to dicts and inject system metadata
        sanitized_items = []
        for idx, item in enumerate(validated_items, start=1):
            llm_content = item.model_dump()
            
            # inject system-managed chunk info (minimal for hierarchical structure)
            chunk_id = f"{guideline_id}_p{page.page_number:03d}_{idx}"
            chunk_info = ChunkInfo(chunk_id=chunk_id)
            
            # nest LLM content under "content" field for clean separation
            final_chunk = {
                "chunk_info": chunk_info.model_dump(),
                "content": llm_content,
                "human_audit": HumanAudit(created_by=extracted_by).model_dump(),
            }
            
            sanitized_items.append(final_chunk)

        raw_path = output_dir / f"page_{page.page_number:03d}_raw.txt"
        write_text(raw_path, raw_text)

        page_json_path = output_dir / f"page_{page.page_number:03d}.json"
        write_json(page_json_path, sanitized_items)

        output = PageOutput(
            page_number=page.page_number,
            raw_text=raw_text,
            parsed_items=sanitized_items,
            validation_errors=[],
            usage=usage,
        )
    
    if completion_callback:
        completion_callback(page.page_number)
    
    return output


async def _process_pdf_async(
    pages: list[PageImage],
    base_prompt: str,
    guideline_id: str,
    guideline_name: str,
    guideline_version: str,
    output_dir: Path,
    client: AnthropicVisionClient,
    extracted_by: str,
    batch_size: int,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[PageOutput]:
    """Process pages in batches asynchronously."""
    outputs: list[PageOutput] = []
    total = len(pages)
    completed = 0

    def _on_page_complete(page_num: int) -> None:
        nonlocal completed
        completed += 1
        if progress_callback:
            progress_callback(completed, total)

    for i in range(0, total, batch_size):
        batch = pages[i : i + batch_size]
        tasks = [
            _process_page(
                page,
                base_prompt,
                guideline_id,
                guideline_name,
                guideline_version,
                output_dir,
                client,
                extracted_by,
                _on_page_complete,
            )
            for page in batch
        ]
        batch_results = await asyncio.gather(*tasks)
        outputs.extend(batch_results)

    return outputs


def process_pages(
    pages: list[PageImage],
    guideline_id: str,
    guideline_name: str,
    guideline_version: str,
    prompt_path: Path,
    output_dir: Path,
    client: AnthropicVisionClient,
    extracted_by: str,
    batch_size: int = 5,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[PageOutput]:
    """Process pre-rendered pages and write outputs to disk."""

    ensure_dir(output_dir)
    base_prompt = load_prompt(prompt_path)

    # run async pipeline in sync context
    return asyncio.run(
        _process_pdf_async(
            pages,
            base_prompt,
            guideline_id,
            guideline_name,
            guideline_version,
            output_dir,
            client,
            extracted_by,
            batch_size,
            progress_callback,
        )
    )


def process_pdf_bytes(
    pdf_bytes: bytes,
    guideline_id: str,
    guideline_name: str,
    guideline_version: str,
    prompt_path: Path,
    output_dir: Path,
    client: AnthropicVisionClient,
    extracted_by: str,
    dpi: int,
    batch_size: int = 5,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[PageOutput]:
    """Process a PDF and write outputs to disk."""

    pages = render_pdf_bytes(pdf_bytes, dpi=dpi)
    return process_pages(
        pages,
        guideline_id,
        guideline_name,
        guideline_version,
        prompt_path,
        output_dir,
        client,
        extracted_by,
        batch_size,
        progress_callback,
    )
