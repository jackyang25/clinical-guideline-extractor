"""PDF to image conversion using PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF


@dataclass(frozen=True)
class PageImage:
    """Rendered page image with metadata."""

    page_number: int
    image_bytes: bytes
    mime_type: str


def render_pdf_bytes(pdf_bytes: bytes, dpi: int) -> list[PageImage]:
    """Render PDF bytes into PNG images for each page."""

    if not pdf_bytes:
        raise ValueError("PDF bytes are empty.")

    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pages: list[PageImage] = []

    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        pixmap = page.get_pixmap(matrix=matrix)
        pages.append(
            PageImage(
                page_number=page_index + 1,
                image_bytes=pixmap.tobytes("png"),
                mime_type="image/png",
            )
        )

    document.close()
    return pages
