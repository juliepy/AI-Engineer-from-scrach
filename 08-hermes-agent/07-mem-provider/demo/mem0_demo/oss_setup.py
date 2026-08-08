"""03 · OSS setup: DeepSeek LLM + local/cloud embedder + Qdrant.

Secrets come from the process environment (and optional demo/.env).
api_key is NOT written into mem0.json — SDKs read env vars.

Embedder selection (MEM0_DEMO_EMBED_PROVIDER):
  - auto (default): OpenAI if OPENAI_API_KEY set, else HuggingFace
    Qwen/Qwen3-Embedding-0.6B (simple local learning default)
  - huggingface: force HF / sentence-transformers
  - ollama: local Ollama embed
  - openai: OpenAI-compatible embed API
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Tuple

from .paths import DEMO_ROOT, HERMES_HOME_DEMO, USER_ID

_DEFAULT_DEEPSEEK_BASE = "https://api.deepseek.com"
_DEFAULT_LLM_MODEL = "deepseek-chat"
_DEFAULT_OPENAI_EMBED_MODEL = "text-embedding-3-small"
_DEFAULT_HF_EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
_DEFAULT_HF_EMBED_DIMS = 1024
_DEFAULT_OLLAMA_EMBED_MODEL = "nomic-embed-text"
_DEFAULT_OLLAMA_URL = "http://localhost:11434"


def load_dotenv_files() -> None:
    """Load KEY=VALUE from demo/.env into os.environ (do not override existing)."""
    for path in (DEMO_ROOT / ".env", HERMES_HOME_DEMO / ".env"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def _env(*names: str, default: str = "") -> str:
    for name in names:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    return default


def _require_env(*names: str, hint: str) -> str:
    val = _env(*names)
    if val:
        return val
    joined = " / ".join(names)
    raise SystemExit(f"Missing env {joined}.\n{hint}")


def _resolve_embed_provider() -> str:
    explicit = _env("MEM0_DEMO_EMBED_PROVIDER", default="auto").lower()
    if explicit in ("huggingface", "hf", "ollama", "openai"):
        return "huggingface" if explicit == "hf" else explicit
    if _env("OPENAI_API_KEY", "MEM0_DEMO_EMBED_API_KEY"):
        return "openai"
    return "huggingface"


def _probe_ollama(base_url: str) -> None:
    url = base_url.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            if resp.status >= 400:
                raise OSError(f"HTTP {resp.status}")
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise SystemExit(
            f"Ollama not reachable at {base_url} ({e}).\n"
            "Start Ollama, then:\n"
            f"  ollama pull {_DEFAULT_OLLAMA_EMBED_MODEL}\n"
            "Or use the default HuggingFace embed (no Ollama):\n"
            "  MEM0_DEMO_EMBED_PROVIDER=huggingface\n"
            "Or set OPENAI_API_KEY for cloud embed."
        ) from e


def _build_openai_embedder() -> Tuple[dict, str]:
    _require_env(
        "OPENAI_API_KEY",
        "MEM0_DEMO_EMBED_API_KEY",
        hint=(
            "MEM0_DEMO_EMBED_PROVIDER=openai but no key.\n"
            "Set OPENAI_API_KEY, or use local HF:\n"
            "  MEM0_DEMO_EMBED_PROVIDER=huggingface"
        ),
    )
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        os.environ["OPENAI_API_KEY"] = _env("MEM0_DEMO_EMBED_API_KEY")

    embed_base = _env("MEM0_DEMO_EMBED_BASE_URL", "OPENAI_BASE_URL") or None
    embed_model = _env("MEM0_DEMO_EMBED_MODEL", default=_DEFAULT_OPENAI_EMBED_MODEL)
    embed_dims = int(_env("MEM0_DEMO_EMBED_DIMS", default="1536"))
    embed_cfg: dict = {
        "model": embed_model,
        "embedding_dims": embed_dims,
    }
    if embed_base:
        embed_cfg["openai_base_url"] = embed_base.rstrip("/")
    label = f"openai-embed ({embed_model})"
    return {"provider": "openai", "config": embed_cfg}, label


def _build_huggingface_embedder() -> Tuple[dict, str]:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "HuggingFace embed needs sentence-transformers:\n"
            "  pip install -r requirements.txt\n"
            f"(default model: {_DEFAULT_HF_EMBED_MODEL})"
        ) from e

    embed_model = _env("MEM0_DEMO_EMBED_MODEL", default=_DEFAULT_HF_EMBED_MODEL)
    # Qwen3-Embedding-0.6B → 1024; override via MEM0_DEMO_EMBED_DIMS if you change model
    default_dims = (
        str(_DEFAULT_HF_EMBED_DIMS)
        if embed_model == _DEFAULT_HF_EMBED_MODEL
        else "1024"
    )
    embed_dims = int(_env("MEM0_DEMO_EMBED_DIMS", default=default_dims))
    embed_cfg = {
        "model": embed_model,
        "embedding_dims": embed_dims,
    }
    label = f"hf-embed ({embed_model}, dims={embed_dims})"
    return {"provider": "huggingface", "config": embed_cfg}, label


def _build_ollama_embedder() -> Tuple[dict, str]:
    ollama_url = _env(
        "MEM0_DEMO_OLLAMA_URL", "OLLAMA_HOST", default=_DEFAULT_OLLAMA_URL
    ).rstrip("/")
    embed_model = _env("MEM0_DEMO_EMBED_MODEL", default=_DEFAULT_OLLAMA_EMBED_MODEL)
    embed_dims = int(_env("MEM0_DEMO_EMBED_DIMS", default="768"))
    _probe_ollama(ollama_url)
    try:
        import ollama  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "Local Ollama embed needs the `ollama` package:\n"
            "  pip install 'ollama>=0.3,<1'"
        ) from e

    embed_cfg = {
        "model": embed_model,
        "ollama_base_url": ollama_url,
        "embedding_dims": embed_dims,
    }
    label = f"ollama-embed ({embed_model} @ {ollama_url})"
    return {"provider": "ollama", "config": embed_cfg}, label


def build_oss_config(qdrant_path: Path) -> Tuple[dict, str]:
    """Build OSS block for mem0.json. Keys stay in env, not in the JSON file."""
    load_dotenv_files()

    _require_env(
        "DEEPSEEK_API_KEY",
        hint=(
            "Set DEEPSEEK_API_KEY in the shell or demo/.env\n"
            "  https://platform.deepseek.com"
        ),
    )
    deepseek_base = _env(
        "DEEPSEEK_API_BASE", "DEEPSEEK_BASE_URL", default=_DEFAULT_DEEPSEEK_BASE
    ).rstrip("/")
    llm_model = _env("MEM0_DEMO_LLM_MODEL", default=_DEFAULT_LLM_MODEL)

    if deepseek_base:
        os.environ.setdefault("DEEPSEEK_API_BASE", deepseek_base)

    llm_cfg: dict = {
        "model": llm_model,
        "deepseek_base_url": deepseek_base,
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    embed_provider = _resolve_embed_provider()
    if embed_provider == "openai":
        embedder, embed_label = _build_openai_embedder()
    elif embed_provider == "ollama":
        embedder, embed_label = _build_ollama_embedder()
    else:
        embedder, embed_label = _build_huggingface_embedder()

    oss = {
        "llm": {"provider": "deepseek", "config": llm_cfg},
        "embedder": embedder,
        "vector_store": {
            "provider": "qdrant",
            "config": {"path": str(qdrant_path)},
        },
    }
    label = f"deepseek ({deepseek_base}) + {embed_label} + local qdrant"
    return oss, label


def prepare_hermes_home() -> Tuple[Path, dict, str]:
    """Create isolated HERMES_HOME + mem0.json (OSS). Does not touch ~/.hermes."""
    hermes_home = HERMES_HOME_DEMO
    hermes_home.mkdir(parents=True, exist_ok=True)
    qdrant_path = hermes_home / "mem0_qdrant"
    qdrant_path.mkdir(parents=True, exist_ok=True)

    oss, label = build_oss_config(qdrant_path)
    mem0_cfg = {
        "mode": "oss",
        "user_id": USER_ID,
        "agent_id": "hermes-demo",
        "oss": oss,
    }
    (hermes_home / "mem0.json").write_text(
        json.dumps(mem0_cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.environ["HERMES_HOME"] = str(hermes_home.resolve())
    os.environ["MEM0_MODE"] = "oss"
    os.environ.pop("MEM0_API_KEY", None)
    os.environ.pop("MEM0_HOST", None)
    return hermes_home, mem0_cfg, label
