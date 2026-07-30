__anchor__ = "document-upload"

from fastapi import FastAPI

from backend.apps.document_upload.app.routers.upload import router

app = FastAPI(title="Document Upload Service", version="0.1.0")
app.include_router(router, prefix="/api/v1")
