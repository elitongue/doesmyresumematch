import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.scoring.engine import score_pair  # noqa: E402


def test_full_match_scores_high():
    job = {'Python': 0.6, 'SQL': 0.4}
    resume = {'Python': 0.6, 'SQL': 0.4}
    score, terms = score_pair(resume, job, ['Python', 'SQL'], 0, {})
    assert score == pytest.approx(100.0)
    assert terms['pcrit'] == 0.0


def test_missing_required_penalizes():
    job = {'Python': 1.0}
    resume = {}
    score, terms = score_pair(resume, job, ['Python'], 0, {})
    assert terms['pcrit'] == 1.0
    assert score == 0.0
