import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI

from backend.startup_log import startup_log


def _log(msg: str) -> None:
    startup_log(f"[llm] {msg}")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

_log("loading .env ...")
load_dotenv()
_log(".env loaded")

# DeepSeek V4 Pro (OpenAI-compatible API)
_log("creating ChatOpenAI (deepseek-v4-pro) ...")
_api_key = os.getenv("DEEPSEEK_API_KEY")
if not _api_key:
    _log("WARNING: DEEPSEEK_API_KEY is empty — set it in .env")
llm = ChatOpenAI(
    model="deepseek-v4-pro",
    api_key=_api_key or "missing-deepseek-api-key",
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    temperature=0.7,
)
_log("ChatOpenAI ready")

# BGE-small-en-v1.5: strong RAG quality, ~130MB, CPU-friendly
# Loaded lazily — importing torch/sentence-transformers on every Streamlit
# startup is the main reason the first page open feels slow.
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "BAAI/bge-small-en-v1.5",
)

DEFAULT_LOCAL_MODEL_DIR = PROJECT_ROOT / "models" / "bge-small-en-v1.5"
LOCAL_EMBEDDING_MODEL_DIR = Path(
    os.getenv("LOCAL_EMBEDDING_MODEL_DIR", str(DEFAULT_LOCAL_MODEL_DIR))
)

_embeddings: "SentenceTransformerEmbeddings | None" = None


def _is_local_model_ready(model_dir: Path) -> bool:
    """A saved SentenceTransformer folder must contain config + weights."""
    return model_dir.is_dir() and (model_dir / "config.json").exists()


def load_or_download_embedding_model(
    hub_name: str = EMBEDDING_MODEL_NAME,
    local_dir: Path = LOCAL_EMBEDDING_MODEL_DIR,
):
    """Load from local disk if present; otherwise download once and save locally."""
    from sentence_transformers import SentenceTransformer

    _log(f"local_dir={local_dir}")
    _log(f"local ready? {_is_local_model_ready(local_dir)}")

    if _is_local_model_ready(local_dir):
        _log("loading SentenceTransformer from local path ...")
        t0 = time.perf_counter()
        model = SentenceTransformer(str(local_dir))
        _log(f"local model loaded in {time.perf_counter() - t0:.1f}s")
        return model

    _log(f"local model missing — downloading hub model: {hub_name}")
    _log("NOTE: this may hang if huggingface.co is unreachable")
    t0 = time.perf_counter()
    model = SentenceTransformer(hub_name)
    _log(f"download+load finished in {time.perf_counter() - t0:.1f}s")

    local_dir.mkdir(parents=True, exist_ok=True)
    _log(f"saving model to {local_dir} ...")
    model.save(str(local_dir))
    _log("model saved")
    return model


class SentenceTransformerEmbeddings(Embeddings):
    """LangChain-compatible wrapper around sentence-transformers."""

    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


def get_embeddings() -> SentenceTransformerEmbeddings:
    """Lazy singleton — torch only loads on first RAG ingest/query."""
    global _embeddings
    if _embeddings is None:
        _log("starting embedding model load (lazy) ...")
        _embeddings = SentenceTransformerEmbeddings(load_or_download_embedding_model())
        _log("embeddings ready")
    return _embeddings
