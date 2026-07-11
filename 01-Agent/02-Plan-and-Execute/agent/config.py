from pathlib import Path


def load_env() -> None:
    """从项目根目录加载 .env（若已安装 python-dotenv）。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
