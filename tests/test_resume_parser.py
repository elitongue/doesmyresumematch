import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.parsing.resume_parser import parse_resume  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / 'apps/api/tests/fixtures'


def _load(name: str) -> bytes:
    return base64.b64decode((FIXTURES / name).read_text())


def test_parse_pdf_resume():
    data = _load('resume1_pdf.txt')
    result = parse_resume(data, 'resume1.pdf')
    assert 'Python' in result['skills']
    assert result['experiences'][0]['start'] == '2020-01'
    assert result['experiences'][0]['end'] == '2022-03'
    assert any('BSc Computer Science' in ed for ed in result['education'])


def test_parse_docx_resume():
    data = _load('resume2_docx.txt')
    result = parse_resume(data, 'resume2.docx')
    assert any('Python' in s for s in result['skills'])
    assert any('MSc AI' in ed for ed in result['education'])

