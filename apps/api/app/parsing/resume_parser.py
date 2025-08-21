import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

SECTION_RE = re.compile(r'^(skills?|experience|projects?|education|certifications?)$', re.I)
DATE_RANGE_RE = re.compile(
    r'(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|\d{4})\s*[\u2013\-]\s*(?P<end>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|\d{4}|Present)',
    re.I,
)
MONTHS = {m.lower(): i + 1 for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}


def _parse_date(part: str) -> Optional[str]:
    part = part.strip()
    if part.lower() == 'present':
        return None
    m = re.match(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', part, re.I)
    if m:
        month = MONTHS[m.group(1).lower()]
        return f"{int(m.group(2)):04d}-{month:02d}"
    m = re.match(r'(\d{4})', part)
    if m:
        return f"{int(m.group(1)):04d}-01"
    return None


def _extract_text_pdf(data: bytes) -> List[str]:
    from pdfminer.high_level import extract_text

    text = extract_text(io.BytesIO(data)) or ""
    return [l.strip() for l in text.splitlines() if l.strip()]


def _extract_text_docx(data: bytes) -> List[str]:
    from docx import Document

    doc = Document(io.BytesIO(data))
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]


def parse_resume(data: bytes, filename: str) -> Dict[str, Any]:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        lines = _extract_text_pdf(data)
    elif ext in {'docx', 'doc'}:
        lines = _extract_text_docx(data)
    else:
        raise ValueError('Unsupported resume format')

    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    prev_line: Optional[str] = None
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        key_match = SECTION_RE.match(lower)
        if key_match:
            current = key_match.group(1).lower()
            sections[current] = []
            if current == 'education' and prev_line:
                sections[current].append(prev_line)
            prev_line = stripped
            continue
        if ":" in stripped:
            head, rest = stripped.split(":", 1)
            if SECTION_RE.match(head.lower()):
                current = head.lower()
                sections[current] = [rest.strip()]
                prev_line = stripped
                continue
        if current:
            sections[current].append(stripped)
        prev_line = stripped

    # Skills
    skills_raw: List[str] = []
    if 'skills' in sections:
        skills_text = ' '.join(sections['skills'])
        skills_raw = [s.strip() for s in re.split(r'[;,\n]', skills_text) if s.strip()]

    # Experience
    experiences: List[Dict[str, Any]] = []
    for line in lines:
        m = DATE_RANGE_RE.search(line)
        if not m or ' at ' not in line:
            continue
        start = _parse_date(m.group('start'))
        end = _parse_date(m.group('end'))
        pre = line[: m.start()].strip()
        role = company = ''
        if ' at ' in pre:
            role, company = pre.split(' at ', 1)
        experiences.append(
            {
                'role': role.strip(),
                'company': company.strip(),
                'start': start,
                'end': end,
                'bullets': [],
            }
        )

    education = sections.get('education', [])
    edu_matches = [
        l for l in lines if re.search(r"\b(BSc|MSc|Bachelor|Master)\b", l, re.I)
    ]
    for l in edu_matches:
        if l not in education:
            education.append(l)
    education = [l for l in education if l and ' at ' not in l]

    certifications = sections.get('certifications', [])

    return {
        'experiences': experiences,
        'skills': skills_raw,
        'education': education,
        'certifications': certifications,
    }

