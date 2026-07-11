import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.server import app
from app.rag import RAGPipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample_docs"


class RAGPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = RAGPipeline()
        self.pipeline.ingest_directory(DATA_DIR)

    def test_ingest_sample_docs(self) -> None:
        self.assertGreater(self.pipeline.chunk_count, 0)

    def test_query_rag_basics(self) -> None:
        result = self.pipeline.query("What is RAG pipeline?", top_k=2)
        self.assertIn("RAG", result.answer)
        self.assertGreaterEqual(len(result.hits), 1)
        doc_ids = {hit["doc_id"] for hit in result.hits}
        self.assertIn("rag_basics", doc_ids)

    def test_query_unknown_topic(self) -> None:
        result = self.pipeline.query("quantum blockchain fusion reactor", top_k=2)
        self.assertIn("未在知识库", result.answer)


class APITests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health(self) -> None:
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["status"], "ok")
        self.assertGreater(body["chunks_indexed"], 0)

    def test_query_endpoint(self) -> None:
        res = self.client.post(
            "/api/query",
            json={"question": "chunking strategy overlap", "top_k": 2},
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("answer", body)
        self.assertGreaterEqual(len(body["hits"]), 1)

    def test_frontend_served(self) -> None:
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("RAG", res.text)


if __name__ == "__main__":
    unittest.main()
