import re
from typing import Any, Dict, List, Optional


def _fetch_url(url: str) -> str:
    import requests
    from readability import Document
    from lxml import html

    resp = requests.get(url, timeout=10)
    doc = Document(resp.text)
    snippet = doc.summary()
    return html.fromstring(snippet).text_content()


def parse_job(source: str) -> Dict[str, Any]:
    if source.strip().startswith("http"):
        text = _fetch_url(source)
    else:
        text = source

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return {}
    title = lines[0]
    body_lower = "\n".join(lines).lower()
    level = None
    for lvl in ["junior", "mid", "senior", "lead"]:
        if re.search(rf"\b{lvl}\b", body_lower):
            level = lvl.capitalize()
            break
    years_required = None
    m = re.search(r"(\d+)\+?\s+years", body_lower)
    if m:
        years_required = int(m.group(1))
    location = None
    work_auth = None
    for line in lines:
        lower = line.lower()
        if lower.startswith("location"):
            location = line.split(":", 1)[1].strip()
        if "visa" in lower or "authorization" in lower:
            work_auth = line

    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    headers = {
        "requirements": "required",
        "preferred": "preferred",
        "nice to have": "preferred",
        "responsibilities": "responsibilities",
    }
    for line in lines[1:]:
        lower = line.lower()
        if lower in headers:
            current = headers[lower]
            sections[current] = []
            continue
        if current and line.startswith(('-', '*')):
            sections[current].append(line.lstrip('-* ').strip())
        elif current and lower in headers:
            current = None

    return {
        "title": title,
        "level": level,
        "years_required": years_required,
        "location": location,
        "work_auth": work_auth,
        "required_skills": sections.get("required", []),
        "preferred_skills": sections.get("preferred", []),
        "responsibilities": sections.get("responsibilities", []),
    }
