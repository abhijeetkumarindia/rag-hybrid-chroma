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
	"""Upload multiple files into a unique per-request folder.

	Returns a unique `upload_id`, `base_path` under `uploads/`, and
	the list of saved relative paths for each file.
	"""
	if not files:
		raise HTTPException(status_code=400, detail="No files provided")

	upload_id = uuid4().hex
	dest_dir = UPLOAD_DIR / upload_id
	dest_dir.mkdir(parents=True, exist_ok=True)

	saved_files = []
	for idx, f in enumerate(files):
		suffix = Path(f.filename).suffix.lower()
		if suffix not in ALLOWED_EXT:
			raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

		# create a collision-resistant name: original_stem + timestamp + index
		timestamp = int(time.time() * 1000)
		safe_stem = Path(f.filename).stem
		dest_name = f"{safe_stem}_{timestamp}_{idx}{suffix}"
		dest_path = dest_dir / dest_name

		content = await f.read()
		with dest_path.open("wb") as out:
			out.write(content)

		# return relative path under uploads for convenience
		rel_path = f"{upload_id}/{dest_name}"
		saved_files.append({"filename": f.filename, "saved_name": dest_name, "relative_path": rel_path})

	return {"uploaded": len(saved_files), "upload_id": upload_id, "base_path": f"uploads/{upload_id}", "files": saved_files}
