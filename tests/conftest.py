import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/marketmind_test.db")
os.environ["ANTHROPIC_API_KEY"] = ""  # tests must never call an LLM
