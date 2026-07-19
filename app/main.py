
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.middleware.request_logger import log_response
from dotenv import load_dotenv 
load_dotenv()

# configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting rag-hybrid-chroma application")
    try:
        yield
    finally:
        logging.info("Shutting down rag-hybrid-chroma application")


def create_app() -> FastAPI:
    app = FastAPI(title="rag-hybrid-chroma REST AI", lifespan=lifespan)
    app.middleware('http')(log_response)
    # main API router (includes v1 sub-routers)
    app.include_router(api_router.api_router)
    # CORS (configure using CORS_ALLOWED_ORIGINS env var, comma-separated)
    allowed = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    if allowed.strip() == "*":
        origins = ["*"]
    else:
        origins = [o.strip() for o in allowed.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def _handle_exceptions(request: Request, exc: Exception):
        logging.exception("Unhandled error in request %s %s", request.method, request.url)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() in ("1", "true", "yes")

    uvicorn.run("app.main:app", host=host, port=port, reload=reload, proxy_headers=True)
