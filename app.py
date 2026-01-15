"""Streamlit UI for clinical guideline extraction."""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import streamlit as st

# ensure current directory is in path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui.extraction_page import render_extraction_page


def _load_dotenv(dotenv_path: Path) -> None:
    """Load environment variables from a .env file."""
    if not dotenv_path.is_file():
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(page_title="Clinical Guideline Extractor", layout="centered")
    _load_dotenv(Path(__file__).resolve().parent / ".env")
    
    # initialize session-specific ID for multi-user support
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]

    st.title("Clinical Guideline Extractor")
    st.caption(
        "Extracts structured clinical content from PDFs using vision AI with predefined schemas. "
        "The model follows ontological definitions for pathways, drug monographs, and reference tables. "
        "AI-extracted content requires human review before clinical use."
    )
    
    # shared paths
    base_output_dir = Path(__file__).resolve().parent / "output"
    prompt_path = Path(__file__).resolve().parent / "schemas" / "content_extraction_prompt.yaml"
    
    render_extraction_page(base_output_dir, prompt_path)


if __name__ == "__main__":
    main()
