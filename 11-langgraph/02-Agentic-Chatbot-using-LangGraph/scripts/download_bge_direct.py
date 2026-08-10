"""Download BAAI/bge-small-en-v1.5 from huggingface.co into models/."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from huggingface_hub import snapshot_download

LOCAL_DIR = ROOT / "models" / "bge-small-en-v1.5"

# Only files needed by sentence-transformers (skip onnx / pytorch pickle)
ALLOW = [
    "1_Pooling/*",
    "config.json",
    "config_sentence_transformers.json",
    "model.safetensors",
    "modules.json",
    "sentence_bert_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
]


def main() -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading BAAI/bge-small-en-v1.5 -> {LOCAL_DIR}")
    print("Endpoint: https://huggingface.co (no mirror)")

    path = snapshot_download(
        repo_id="BAAI/bge-small-en-v1.5",
        local_dir=str(LOCAL_DIR),
        allow_patterns=ALLOW,
        endpoint="https://huggingface.co",
    )
    print(f"Done: {path}")
    print("Files:")
    for p in sorted(LOCAL_DIR.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(LOCAL_DIR)} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
