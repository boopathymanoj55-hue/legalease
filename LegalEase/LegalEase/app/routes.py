from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.ai_core.gemini_generator import GeminiDocumentGenerator
from app.config import get_settings
from app.schemas import DocumentRequest, DocumentResponse, ExportRequest
from app.services.document_service import format_docx, format_pdf, sanitize_text

router = APIRouter()
settings = get_settings()
generator = GeminiDocumentGenerator(settings)


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "ai_configured": generator.configured,
        "model": settings.gemini_model,
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_document(payload: DocumentRequest) -> DocumentResponse:
    try:
        total = len(payload.document_type) + len(payload.parties) + len(payload.terms) + len(payload.dates)
        if total > settings.max_input_chars:
            raise HTTPException(status_code=413, detail="Input is too large.")

        content = generator.generate_document(
            document_type=payload.document_type,
            parties=payload.parties,
            terms=payload.terms,
            dates=payload.dates,
            language=payload.language,
        )
        return DocumentResponse(
            document_type=payload.document_type,
            content=sanitize_text(content),
            model=settings.gemini_model if generator.configured else "demo-mode",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Document generation failed: {exc}") from exc


@router.post("/export/txt")
def export_txt(payload: ExportRequest):
    content = sanitize_text(payload.content)
    return PlainTextResponse(
        content,
        headers={
            "Content-Disposition": 'attachment; filename="legalease_document.txt"'
        },
    )


@router.post("/export/docx")
def export_docx(payload: ExportRequest):
    temp_dir = Path(tempfile.mkdtemp(prefix="legalease_"))
    path = temp_dir / "legalease_document.docx"
    try:
        format_docx(payload.content, payload.document_type, path)
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="legalease_document.docx",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DOCX export failed: {exc}") from exc


@router.post("/export/pdf")
def export_pdf(payload: ExportRequest):
    temp_dir = Path(tempfile.mkdtemp(prefix="legalease_"))
    path = temp_dir / "legalease_document.pdf"
    try:
        format_pdf(payload.content, payload.document_type, path)
        return FileResponse(path, media_type="application/pdf", filename="legalease_document.pdf")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {exc}") from exc
