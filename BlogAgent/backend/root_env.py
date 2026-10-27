"""Load the repo-root `.env` so backend works regardless of cwd (Docker, uvicorn, etc.)."""

from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")
