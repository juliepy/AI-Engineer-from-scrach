from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.startup_log import startup_log

startup_log("probe ok")
print("startup_log written ->", ROOT / "logs" / "startup.log")

from backend.llm import embeddings

print("embeddings ok", type(embeddings))
