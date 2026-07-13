from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from pathlib import Path
from uuid import uuid4
import time

router = APIRouter()

ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".pdf", ".txt", ".csv", ".docx", ".doc"}


@router.post(
    "/upload",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "files": {
                                "type": "array",
                                "items": {"type": "string", "format": "binary"},
                            }
                        },
                        "required": ["files"],
                    }
                }
            }
        }
    },
)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files directly into the uploads folder.
    """

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    saved_files = []

    for idx, f in enumerate(files):
        suffix = Path(f.filename).suffix.lower()

        if suffix not in ALLOWED_EXT:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}"
            )

        timestamp = int(time.time() * 1000)
        unique_id = uuid4().hex[:8]

        safe_name = (
            f"{Path(f.filename).stem}_{timestamp}_{unique_id}{suffix}"
        )

        dest_path = UPLOAD_DIR / safe_name

        with dest_path.open("wb") as out:
            out.write(await f.read())

        saved_files.append(
            {
                "original_filename": f.filename,
                "saved_name": safe_name,
                "path": str(dest_path),
            }
        )

    return {
        "uploaded": len(saved_files),
        "upload_dir": str(UPLOAD_DIR),
        "files": saved_files,
    }