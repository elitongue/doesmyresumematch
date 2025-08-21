import sys
from pathlib import Path
import math
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.scoring import vectors  # noqa: E402


def test_job_weights_normalization():
    posting = 'Python experience required. SQL preferred.'
    w = vectors.job_skill_weights(posting, ['Python'], ['SQL'])
    assert abs(sum(w.values()) - 1.0) < 1e-6
    assert w['Python'] > w['SQL']


def test_resume_weights_decay(monkeypatch):
    class Fixed(datetime):
        @classmethod
        def utcnow(cls):
            return cls(2024, 1, 1)
    monkeypatch.setattr(vectors, 'datetime', Fixed)
    instances = [
        {'name': 'Python', 'start': '2020-01', 'end': '2022-01'},
        {'name': 'SQL', 'start': '2023-01', 'end': '2023-06'},
    ]
    w, ev = vectors.resume_skill_weights(instances)
    norm = math.sqrt(sum(v*v for v in w.values()))
    assert abs(norm - 1.0) < 1e-6
    assert ev['Python']['months_since_last_use'] == 24
    assert ev['SQL']['months_since_last_use'] == 7
    assert w['Python'] > w['SQL']

