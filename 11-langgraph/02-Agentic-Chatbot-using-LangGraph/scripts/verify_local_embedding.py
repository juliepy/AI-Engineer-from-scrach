from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.llm import LOCAL_EMBEDDING_MODEL_DIR, embeddings

print("local_dir:", LOCAL_EMBEDDING_MODEL_DIR)
print("config exists:", (LOCAL_EMBEDDING_MODEL_DIR / "config.json").exists())
vec = embeddings.embed_query("hello")
print("ok dim:", len(vec))
