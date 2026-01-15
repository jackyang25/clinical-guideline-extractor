"""Text parsing and prompt management for LLM interactions."""

from __future__ import annotations

import json
from pathlib import Path


class PromptLoadError(RuntimeError):
    """Raised when a prompt cannot be loaded."""


class ExtractionError(RuntimeError):
    """Raised when extraction fails."""


# common VLM encoding corruptions: corrupted -> original
# these occur when UTF-8 text is misinterpreted as Latin-1
ENCODING_FIXES: list[tuple[str, str]] = [
    ("\u00e2\u0086\u0092", "\u2192"),  # right arrow
    ("\u00e2\u0089\u00a5", "\u2265"),  # greater than or equal
    ("\u00e2\u0089\u00a4", "\u2264"),  # less than or equal
    ("\u00c2\u00b0", "\u00b0"),        # degree symbol
    ("\u00c2\u00b5", "\u00b5"),        # micro symbol
    ("\u00e2\u0080\u0093", "\u2013"),  # en dash
    ("\u00e2\u0080\u0094", "\u2014"),  # em dash
    ("\u00e2\u0080\u0099", "\u2019"),  # right single quote
    ("\u00e2\u0080\u0098", "\u2018"),  # left single quote
    ("\u00e2\u0080\u009c", "\u201c"),  # left double quote
    ("\u00e2\u0080\u009d", "\u201d"),  # right double quote
    ("\u00c3\u00a9", "\u00e9"),        # e acute
    ("\u00c3\u00a8", "\u00e8"),        # e grave
    ("\u00c3\u00bc", "\u00fc"),        # u umlaut
    ("\u00c3\u00b6", "\u00f6"),        # o umlaut
    ("\u00c3\u00a4", "\u00e4"),        # a umlaut
    ("\u00c3\u00b1", "\u00f1"),        # n tilde
    ("\u00c2\u00b9", "\u00b9"),        # superscript 1
    ("\u00c2\u00b2", "\u00b2"),        # superscript 2
    ("\u00c2\u00b3", "\u00b3"),        # superscript 3
]


def fix_encoding(text: str) -> str:
    """Fix common UTF-8/Latin-1 encoding corruptions from VLM output.
    
    VLMs sometimes output text with encoding issues, particularly for
    special characters like arrows, comparison symbols, and degree symbols.
    This function applies known fixes.
    """
    result = text
    for corrupted, original in ENCODING_FIXES:
        result = result.replace(corrupted, original)
    return result


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
    """Parse a JSON array from the model response.
    
    Applies encoding fixes before parsing to handle VLM output corruption.
    """
    # fix encoding issues before parsing
    fixed_text = fix_encoding(raw_text)
    cleaned = strip_json_fence(fixed_text)
    
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ExtractionError("Model response is not valid JSON.") from exc

    if not isinstance(payload, list):
        raise ExtractionError("Model response must be a JSON array.")

    return payload
