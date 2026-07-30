import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
model: SentenceTransformer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    device = os.getenv("DEVICE", "cpu")
    model = SentenceTransformer(MODEL_NAME, device=device, trust_remote_code=True)
    yield


app = FastAPI(lifespan=lifespan, title="Embedding Service")


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]
    dim: int


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    vec = model.encode(req.text, normalize_embeddings=True)
    return EmbedResponse(embedding=vec.tolist(), dim=len(vec))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5100)
