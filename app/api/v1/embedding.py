from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from app.core.dependencies import initial_indexes

router = APIRouter(prefix="/embedding-actions", tags=["embedding-actions"])


@router.post("/initial-indexes")
async def initial_indexes_action(background_tasks: BackgroundTasks):
	"""Trigger building/initializing of indexes and return the number of indexed vectors."""
	try:
		# schedule the indexing task; do not call it synchronously here
		background_tasks.add_task(initial_indexes)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

	return JSONResponse(status_code=200, content={"msg": "Indexing scheduled"})
