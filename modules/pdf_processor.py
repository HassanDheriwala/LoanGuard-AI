"""
PDF Processor — extracts plain text from uploaded loan agreement PDFs.
Returns structured results for the Streamlit UI and future FastAPI endpoints.
"""

import re
from dataclasses import dataclass
from io import BytesIO


@dataclass
class PdfExtractionResult:
    """Structured output from PDF text extraction."""

    success: bool
    text: str
    filename: str
    page_count: int
    char_count: int
    word_count: int
    error: str = ""


def _clean_extracted_text(text: str) -> str:
    """Normalize whitespace and line breaks for downstream NLP analysis."""
    # Join words split across lines with a hyphen (e.g. "proc-\nessing")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse extra blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim trailing spaces on each line
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def process_pdf_upload(pdf_file) -> PdfExtractionResult:
    """
    Extract and clean text from an uploaded PDF file.

    Args:
        pdf_file: Streamlit UploadedFile or any file-like object with PDF bytes.

    Returns:
        PdfExtractionResult with text ready for analyze_loan_text().
    """
    filename = getattr(pdf_file, "name", "uploaded.pdf")

    try:
        from pypdf import PdfReader
    except ImportError:
        return PdfExtractionResult(
            success=False,
            text="",
            filename=filename,
            page_count=0,
            char_count=0,
            word_count=0,
            error="pypdf is not installed. Run: pip install pypdf",
        )

    try:
        if hasattr(pdf_file, "read"):
            raw = pdf_file.read()
            if hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
            buffer = BytesIO(raw)
        else:
            buffer = BytesIO(pdf_file)

        reader = PdfReader(buffer)
        page_count = len(reader.pages)
        pages: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text.strip())

        if not pages:
            return PdfExtractionResult(
                success=False,
                text="",
                filename=filename,
                page_count=page_count,
                char_count=0,
                word_count=0,
                error=(
                    "No readable text found. This PDF may be scanned/image-only. "
                    "Try a text-based PDF or paste the agreement manually."
                ),
            )

        combined = _clean_extracted_text("\n\n".join(pages))
        word_count = len(combined.split())

        return PdfExtractionResult(
            success=True,
            text=combined,
            filename=filename,
            page_count=page_count,
            char_count=len(combined),
            word_count=word_count,
        )

    except Exception as exc:
        return PdfExtractionResult(
            success=False,
            text="",
            filename=filename,
            page_count=0,
            char_count=0,
            word_count=0,
            error=f"Could not read PDF: {exc}",
        )


def extract_text_from_pdf(pdf_file) -> str:
    """
    Backward-compatible helper — returns extracted text or an error string.
    """
    result = process_pdf_upload(pdf_file)
    if result.success:
        return result.text
    return f"[PDF Error] {result.error}"
