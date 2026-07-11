from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.rag import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample_docs"
FRONTEND_DIR = ROOT / "frontend"

pipeline = RAGPipeline()
pipeline.ingest_directory(DATA_DIR)

app = FastAPI(title="RAG Harness Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class IngestRequest(BaseModel):
    doc_id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=20000)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "chunks_indexed": pipeline.chunk_count,
        "sample_docs": sorted(p.stem for p in DATA_DIR.glob("*.txt")),
    }


@app.post("/api/query")
def query(req: QueryRequest) -> dict:
    result = pipeline.query(req.question, top_k=req.top_k)
    return {
        "query": result.query,
        "answer": result.answer,
        "hits": result.hits,
    }


@app.post("/api/ingest")
def ingest(req: IngestRequest) -> dict:
    added = pipeline.ingest_text(req.doc_id, req.text)
    return {"doc_id": req.doc_id, "chunks_added": added, "total_chunks": pipeline.chunk_count}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
