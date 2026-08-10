"""Download BGE embedding model once and save under models/."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.llm import LOCAL_EMBEDDING_MODEL_DIR, load_or_download_embedding_model

if __name__ == "__main__":
    model = load_or_download_embedding_model()
    print(f"Ready: {LOCAL_EMBEDDING_MODEL_DIR} (dim={model.get_sentence_embedding_dimension()})")
