import json
import os
import time
from datetime import datetime, timezone

from fastapi import Request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "monitoring" / "audit.json"

async def log_response(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start

    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.url.path,
        "query": dict(request.query_params),
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "client": request.client.host if request.client else None,
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

    return response