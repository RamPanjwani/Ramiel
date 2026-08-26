"""File ingestion and session upload endpoints.

Phase 0: stub accepting uploads, storing nothing.
Phase 3+: will persist to data/uploads/ and feed into OCR/vision pipeline.
"""

from fastapi import APIRouter, UploadFile

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_file(file: UploadFile) -> dict[str, str]:
    """Accept a file upload.

    Phase 0 stub — acknowledges receipt without processing.
    """
    return {
        "status": "received",
        "filename": file.filename or "unknown",
        "message": "Upload endpoint active (Phase 0 stub — file not persisted).",
    }
