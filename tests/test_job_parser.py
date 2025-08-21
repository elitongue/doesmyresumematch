import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.parsing.job_parser import parse_job  # noqa: E402

POSTING1 = """Software Engineer\nLocation: Remote\nRequirements\n- Python\n- SQL\nPreferred\n- Docker\nResponsibilities\n- Build systems\n"""

POSTING2 = """Data Scientist\nRequirements\n- Machine Learning\nPreferred\n- R\n- SQL\n"""


def test_parse_job_required_preferred():
    job = parse_job(POSTING1)
    assert job['title'] == 'Software Engineer'
    assert job['required_skills'] == ['Python', 'SQL']
    assert job['preferred_skills'] == ['Docker']
    assert job['responsibilities'] == ['Build systems']


def test_parse_job_deterministic():
    job1 = parse_job(POSTING2)
    job2 = parse_job(POSTING2)
    assert job1['required_skills'] == job2['required_skills'] == ['Machine Learning']
    assert job1['preferred_skills'] == job2['preferred_skills'] == ['R', 'SQL']

