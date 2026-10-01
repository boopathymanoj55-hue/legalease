from pathlib import Path

from app.services.document_service import format_docx, format_pdf, sanitize_text


SAMPLE = """1. PARTIES

Alice (Disclosing Party) and Bob (Receiving Party).

2. TERMS

Confidential information must be protected.
"""


def test_sanitize_text():
    assert sanitize_text("hello\u2014world") == "hello-world"


def test_docx_export(tmp_path: Path):
    path = format_docx(SAMPLE, "NDA", tmp_path / "test.docx")
    assert path.exists()
    assert path.stat().st_size > 1000


def test_pdf_export(tmp_path: Path):
    path = format_pdf(SAMPLE, "NDA", tmp_path / "test.pdf")
    assert path.exists()
    assert path.stat().st_size > 500
