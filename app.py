"""Streamlit UI for clinical guideline extraction."""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from schemas.base_models import GuidelineInfo, HumanAudit
from extraction.formatters import wrap_guideline_output, wrap_page_output
from extraction.llm.client import AnthropicVisionClient
from extraction.metadata_extractor import extract_metadata
from extraction.pipeline import process_pages
from extraction.processors.pdf import render_pdf_bytes
from extraction.utils import ensure_dir, write_json


# pricing per million tokens (USD)
MODEL_PRICING = {
    "claude-3-5-haiku-20241022": {
        "input": 0.80,
        "output": 4.00,
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-opus-4-20250514": {
        "input": 15.00,
        "output": 75.00,
    },
    "claude-opus-4-1-20250805": {
        "input": 15.00,
        "output": 75.00,
    },
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Calculate estimated cost for a model. Returns None if pricing unavailable."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


@dataclass(frozen=True)
class UploadedPdf:
    """Container for uploaded PDF data."""

    filename: str
    size_bytes: int
    sha256_hex: str
    content: bytes


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


def _read_uploaded_pdf() -> UploadedPdf | None:
    """Read and validate uploaded PDF file."""
    uploaded = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload a PDF. The conversion step is a placeholder for now.",
    )
    if uploaded is None:
        return None

    content = uploaded.getvalue()
    if not content:
        raise ValueError("Uploaded file is empty.")

    sha256_hex = hashlib.sha256(content).hexdigest()
    return UploadedPdf(
        filename=uploaded.name,
        size_bytes=len(content),
        sha256_hex=sha256_hex,
        content=content,
    )


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(page_title="Clinical Guideline Extractor", layout="centered")
    _load_dotenv(Path(__file__).resolve().parent / ".env")

    st.title("Clinical Guideline Extractor")
    st.caption("Upload a PDF and extract structured clinical content.")

    try:
        pdf = _read_uploaded_pdf()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return

    st.subheader("Vision settings")
    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="Add your API key to enable extraction.",
    )
    model_name = st.text_input(
        "Model name",
        value="claude-sonnet-4-20250514",
        help="Popular models: claude-sonnet-4-20250514, claude-3-5-haiku-20241022 (faster), claude-opus-4-20250514 (best)",
    )
    max_tokens = st.number_input("Max tokens", min_value=256, max_value=16384, value=4000)
    batch_size = st.number_input(
        "Batch size",
        min_value=1,
        max_value=20,
        value=5,
        help="Number of pages to process in parallel. Higher = faster but more API load.",
    )
    dpi = st.number_input("Render DPI", min_value=100, max_value=400, value=200)

    created_by = st.text_input(
        "Your name/email",
        value=os.getenv("USER", ""),
        help="Who is running this extraction (e.g., your name or email)",
    )

    # output settings (fixed paths)
    output_dir = Path(__file__).resolve().parent / "output"
    prompt_path = Path(__file__).resolve().parent / "schemas" / "content_extraction_prompt.yaml"

    if pdf is None:
        st.info("Choose a PDF to get started.")
        return

    st.subheader("File details")
    st.write(
        {
            "filename": pdf.filename,
            "size_bytes": pdf.size_bytes,
            "sha256": pdf.sha256_hex,
        }
    )
    st.caption("Output will be saved to: ./output/")

    if st.button("Run extraction", type="primary", use_container_width=True):
        if not api_key:
            st.error("Provide an Anthropic API key to continue.")
            return

        try:
            ensure_dir(output_dir)
            
            # clean up previous extraction outputs
            for file in output_dir.glob("*"):
                if file.is_file():
                    file.unlink()

            # step 1: extract metadata from first page
            metadata_status = st.info("Step 1/2: Extracting metadata from first page...")
            metadata_client = AnthropicVisionClient(api_key, model_name, max_tokens=1000)
            first_page = render_pdf_bytes(pdf.content, dpi=150)[0]  # lower DPI for speed
            auto_metadata = extract_metadata(first_page, metadata_client)
            
            # generate guideline info from metadata
            guideline_id = auto_metadata.guideline_name.lower().replace(" ", "_")[:50]
            guideline_name = auto_metadata.guideline_name
            guideline_version = auto_metadata.guideline_version
            country = auto_metadata.country
            jurisdiction = auto_metadata.jurisdiction
            organization = auto_metadata.organization
            regulatory_status = "draft"
            
            metadata_status.success(f"Metadata extracted: {guideline_name} v{guideline_version}")
            
            # step 2: render PDF pages and extract content
            init_status = st.info("Step 2/2: Rendering PDF pages...")
            pages = render_pdf_bytes(pdf.content, dpi=int(dpi))
            total_pages = len(pages)
            init_status.success(f"Starting extraction for {total_pages} pages (batch size: {int(batch_size)})")

            progress = st.progress(0, text="Starting...")
            status = st.empty()

            def _update_progress(current: int, total: int) -> None:
                progress.progress(current / total, text=f"Completed {current} of {total} pages")
                status.info(f"{current} completed | {total - current} remaining")

            client = AnthropicVisionClient(
                api_key=api_key,
                model=model_name,
                max_tokens=int(max_tokens),
            )
            page_outputs = process_pages(
                pages=pages,
                guideline_id=guideline_id,
                guideline_name=guideline_name,
                guideline_version=guideline_version,
                prompt_path=prompt_path,
                output_dir=output_dir,
                client=client,
                extracted_by=created_by,
                batch_size=int(batch_size),
                progress_callback=_update_progress,
            )
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            return

        all_items: list[dict] = []
        all_items_flat: list[dict] = []  # for RAG with full context
        error_count = 0
        total_input_tokens = 0
        total_output_tokens = 0
        pages_wrapped = []
        
        for output in page_outputs:
            all_items.extend(output.parsed_items)
            error_count += len(output.validation_errors)
            total_input_tokens += output.usage.get("input_tokens", 0)
            total_output_tokens += output.usage.get("output_tokens", 0)
            
            # create flattened chunks with full context for RAG
            for chunk in output.parsed_items:
                flat_chunk = {
                    "chunk_id": chunk["chunk_info"]["chunk_id"],
                    "guideline_id": guideline_id,
                    "guideline_name": guideline_name,
                    "guideline_version": guideline_version,
                    "page": output.page_number,
                    "content": chunk["content"],
                    "human_audit": chunk["human_audit"],
                }
                all_items_flat.append(flat_chunk)
            
            # wrap each page with metadata
            has_errors = len(output.validation_errors) > 0
            page_wrapped = wrap_page_output(
                page_number=output.page_number,
                chunks=output.parsed_items,
                extracted_by=created_by,
                extraction_status="validation_failed" if has_errors else "success",
                needs_retry=has_errors,
            )
            pages_wrapped.append(page_wrapped)
        
        # create guideline info and audit
        guideline_info = GuidelineInfo(
            guideline_id=guideline_id,
            guideline_name=guideline_name,
            guideline_version=guideline_version,
            country=country,
            jurisdiction=jurisdiction,
            organization=organization,
            regulatory_status=regulatory_status,
        )
        guideline_audit = HumanAudit(created_by=created_by)
        
        # wrap all pages with guideline info and audit
        full_output = wrap_guideline_output(
            guideline_info=guideline_info,
            guideline_audit=guideline_audit,
            pages=pages_wrapped,
        )
        
        # save flat chunks with full context (for RAG)
        combined_path = output_dir / "guideline_chunks_flat.json"
        write_json(combined_path, all_items_flat)
        
        # save structured output with full metadata
        structured_path = output_dir / "guideline_with_metadata.json"
        write_json(structured_path, full_output)

        # calculate pages needing retry and collect errors
        pages_needing_retry = [p["page_info"]["page_number"] for p in pages_wrapped if p["page_info"]["needs_retry"]]
        
        if pages_needing_retry:
            st.warning(
                f"Extraction complete with failures. Pages: {len(page_outputs)}. "
                f"Content items: {len(all_items_flat)}. "
                f"Pages needing retry: {len(pages_needing_retry)} (pages {', '.join(map(str, pages_needing_retry))})"
            )
            
            # show validation errors
            st.subheader("Validation Errors")
            for output in page_outputs:
                if output.validation_errors:
                    with st.expander(f"Page {output.page_number} - {len(output.validation_errors)} error(s)"):
                        for error in output.validation_errors:
                            st.error(error)
        else:
            st.success(
                f"Extraction complete. Pages: {len(page_outputs)}. "
                f"Content items: {len(all_items_flat)}. All pages validated successfully."
            )
        
        st.subheader("API Usage Statistics")
        
        estimated_cost = calculate_cost(model_name, total_input_tokens, total_output_tokens)
        
        # debug info
        st.caption(f"Model: {model_name} | Cost: {estimated_cost if estimated_cost is not None else 'None'}")
        
        if estimated_cost is not None:
            col1, col2, col3, col4, col5 = st.columns(5)
        else:
            col1, col2, col3, col4 = st.columns(4)
            
        with col1:
            st.metric("API Requests", len(page_outputs))
        with col2:
            st.metric("Input Tokens", f"{total_input_tokens:,}")
        with col3:
            st.metric("Output Tokens", f"{total_output_tokens:,}")
        with col4:
            st.metric("Total Tokens", f"{total_input_tokens + total_output_tokens:,}")
            
        if estimated_cost is not None:
            with col5:
                st.metric("Est. Cost (USD)", f"${estimated_cost:.4f}")
        else:
            supported_models = ", ".join(MODEL_PRICING.keys())
            st.caption(f"Cost estimation unavailable for {model_name}")
            with st.expander("Supported models for cost estimation"):
                st.text(supported_models)
        
        st.success("Files saved to: ./output/")
        
        st.subheader("Extraction metadata")
        
        st.caption("GuidelineInfo")
        st.json({
            "guideline_id": guideline_info.guideline_id,
            "guideline_name": guideline_info.guideline_name,
            "guideline_version": guideline_info.guideline_version,
            "country": guideline_info.country,
            "jurisdiction": guideline_info.jurisdiction,
            "organization": guideline_info.organization,
            "regulatory_status": guideline_info.regulatory_status,
        })
        
        st.caption("HumanAudit")
        st.json({
            "status": guideline_audit.status,
            "version": guideline_audit.version,
            "created_at": guideline_audit.created_at,
            "created_by": guideline_audit.created_by,
            "reviewed_by": guideline_audit.reviewed_by,
            "approval_date": guideline_audit.approval_date,
            "notes": guideline_audit.notes,
        })
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "Download Chunks Only (Flat)",
                data=combined_path.read_text(encoding="utf-8"),
                file_name="guideline_chunks_flat.json",
                mime="application/json",
                use_container_width=True,
                help="Array of self-contained chunks with denormalized guideline info (for RAG/database import)",
            )
        with col_dl2:
            st.download_button(
                "Download Guideline with Metadata",
                data=structured_path.read_text(encoding="utf-8"),
                file_name="guideline_with_metadata.json",
                mime="application/json",
                use_container_width=True,
                help="Full hierarchical structure: guideline → pages → chunks with all metadata",
            )

        st.subheader("Extracted content")
        if all_items_flat:
            # group by page number
            from collections import defaultdict
            pages_dict = defaultdict(list)
            content_type_counts = defaultdict(int)
            
            for item in all_items_flat:
                page_num = item.get('page', 0)
                pages_dict[page_num].append(item)
                content_type = item.get('content', {}).get('content_type', 'unknown')
                content_type_counts[content_type] += 1
            
            # show content type summary
            summary_parts = [f"{count} {ctype.replace('_', ' ')}" for ctype, count in sorted(content_type_counts.items())]
            st.caption(f"Total items: {len(all_items_flat)} ({', '.join(summary_parts)})")
            
            # display grouped by page
            for page_num in sorted(pages_dict.keys()):
                items = pages_dict[page_num]
                with st.expander(f"Page {page_num} ({len(items)} item{'s' if len(items) != 1 else ''})"):
                    for idx, item in enumerate(items, start=1):
                        content = item.get('content', {})
                        content_type = content.get('content_type', 'unknown')
                        topic = content.get('topic', 'Unknown')
                        
                        # build title based on content type
                        if content_type == 'clinical_pathway':
                            scenario = content.get('specific_scenario', '')
                            title = f"**{idx}. [{content_type}] {topic} - {scenario}**"
                        elif content_type == 'reference_table':
                            table_name = content.get('table_name', '')
                            title = f"**{idx}. [{content_type}] {topic}: {table_name}**"
                        elif content_type == 'drug_monograph':
                            drug_name = content.get('drug_name', '')
                            title = f"**{idx}. [{content_type}] {drug_name}**"
                        elif content_type == 'generic':
                            section_type = content.get('section_type', '')
                            title = f"**{idx}. [{content_type}] {topic} ({section_type})**"
                        else:
                            title = f"**{idx}. [{content_type}] {topic}**"
                        
                        st.markdown(title)
                        st.json(item)
                        if idx < len(items):
                            st.divider()
        else:
            st.warning("No content extracted.")


if __name__ == "__main__":
    main()
