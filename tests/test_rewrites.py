import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.llm.rewrites import suggest_rewrites  # noqa: E402


def fake_llm(prompt: str) -> str:
    return "1. Improved bullet\n2. Another"


def test_suggest_rewrites():
    bullets = ["Did something"]
    skills = ["Python"]
    out = suggest_rewrites(bullets, skills, llm_fn=fake_llm)
    assert out == ["Improved bullet", "Another"]


def test_empty_input_returns_empty():
    assert suggest_rewrites([], ["Python"], llm_fn=fake_llm) == []
