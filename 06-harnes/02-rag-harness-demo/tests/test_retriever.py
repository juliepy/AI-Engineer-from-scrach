import unittest

from app.chunker import chunk_text
from app.indexer import TfidfIndex


class RetrieverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = TfidfIndex()
        chunks = chunk_text(
            "rag_basics",
            "RAG combines retrieval and generation for knowledge QA.",
        )
        chunks += chunk_text(
            "chunking",
            "Chunking splits long documents into smaller overlapping segments.",
        )
        self.index.add_chunks(chunks)

    def test_search_returns_relevant_doc(self) -> None:
        hits = self.index.search("retrieval generation", top_k=2)
        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(hits[0].chunk.doc_id, "rag_basics")

    def test_search_chunking_query(self) -> None:
        hits = self.index.search("overlapping segments", top_k=1)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].chunk.doc_id, "chunking")

    def test_empty_query_returns_empty(self) -> None:
        self.assertEqual(self.index.search(""), [])


if __name__ == "__main__":
    unittest.main()
