import unittest

from app.chunker import chunk_text


class ChunkerTests(unittest.TestCase):
    def test_empty_text_returns_no_chunks(self) -> None:
        self.assertEqual(chunk_text("doc", ""), [])
        self.assertEqual(chunk_text("doc", "   \n  "), [])

    def test_short_text_single_chunk(self) -> None:
        chunks = chunk_text("doc", "hello world", chunk_size=50, overlap=10)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].doc_id, "doc")
        self.assertEqual(chunks[0].text, "hello world")

    def test_overlap_produces_multiple_chunks(self) -> None:
        text = "a" * 250
        chunks = chunk_text("doc", text, chunk_size=100, overlap=20)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0].index, 0)
        self.assertEqual(chunks[1].index, 1)

    def test_invalid_overlap_raises(self) -> None:
        with self.assertRaises(ValueError):
            chunk_text("doc", "abc", chunk_size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
