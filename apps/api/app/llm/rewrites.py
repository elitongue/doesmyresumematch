from collections import defaultdict
from typing import Callable, Dict, List

from openai import OpenAI

SYSTEM_PROMPT = (
    "rewrite for clarity and measurable impact; do not invent facts; "
    "keep only info present in the bullet."
)


_MODEL_USAGE: Dict[str, int] = defaultdict(int)


def get_model_usage() -> Dict[str, int]:
    return dict(_MODEL_USAGE)


def _openai_call(prompt: str) -> str:
    client = OpenAI()
    model = "gpt-3.5-turbo"  # small context window
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=256,
    )
    _MODEL_USAGE[model] += 1
    return resp.choices[0].message.content.strip()


def suggest_rewrites(
    resume_bullets: List[str],
    target_skills: List[str],
    llm_fn: Callable[[str], str] | None = None,
) -> List[str]:
    if not resume_bullets or not target_skills:
        return []
    llm_fn = llm_fn or _openai_call
    prompt = (
        "Target skills: " + ", ".join(target_skills) + "\n" + "\n".join(resume_bullets)
    )
    try:
        out = llm_fn(prompt)
    except Exception:
        return []
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bullets: List[str] = []
    for line in lines:
        if line[0].isdigit() and "." in line:
            line = line.split(".", 1)[1].strip()
        bullets.append(line)
    if len(bullets) < 3:
        return bullets
    return bullets[:5]
