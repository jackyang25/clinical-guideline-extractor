"""Text parsing and prompt management for LLM interactions."""

from __future__ import annotations

import json
from pathlib import Path


class PromptLoadError(RuntimeError):
    """Raised when a prompt cannot be loaded."""


class ExtractionError(RuntimeError):
    """Raised when extraction fails."""


def load_prompt(prompt_path: Path) -> str:
    """Load a prompt file into memory."""

    if not prompt_path.is_file():
        raise PromptLoadError(f"Prompt file not found: {prompt_path}")

    content = prompt_path.read_text(encoding="utf-8").strip()
    if not content:
        raise PromptLoadError(f"Prompt file is empty: {prompt_path}")

    return content


def build_prompt(
    base_prompt: str,
    guideline_id: str,
    guideline_name: str,
    guideline_version: str,
    page_number: int,
) -> str:
    """Attach guideline context to the base prompt."""

    context = f"""
Guideline Context:
- guideline_id: {guideline_id}
- guideline_name: {guideline_name}
- guideline_version: {guideline_version}
- page: {page_number}
"""
    return f"{base_prompt}\n{context}"


def strip_json_fence(text: str) -> str:
    """Remove markdown JSON fences if present."""

    if "```json" in text:
        return text.split("```json", 1)[1].split("```", 1)[0].strip()
    if "```" in text:
        return text.split("```", 1)[1].split("```", 1)[0].strip()
    return text.strip()


def parse_json_response(raw_text: str) -> list[dict]:
    """Parse a JSON array from the model response."""

    cleaned = strip_json_fence(raw_text)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ExtractionError("Model response is not valid JSON.") from exc

    if not isinstance(payload, list):
        raise ExtractionError("Model response must be a JSON array.")

    return payload
