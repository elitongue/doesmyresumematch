import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.matching.skill_matcher import SkillMatcher  # noqa: E402


def fake_embed(text: str):
    vectors = {
        'python': [1, 0],
        'machine learning': [0, 1],
        'ml': [0, 1],
        'deep learning': [1, 1],
        'deeplearning': [0.9, 0.9],
    }
    return vectors.get(text.lower(), [0, 0])


def test_skill_matcher_exact_alias_embedding():
    matcher = SkillMatcher(embedding_fn=fake_embed)
    cands = [
        {'text': 'Python', 'snippet': 'Python snippet'},
        {'text': 'ml', 'snippet': 'ml snippet', 'start': '2021-01', 'end': '2022-01'},
        {'text': 'deeplearning', 'snippet': 'deeplearning'},
        {'text': 'randomstuff', 'snippet': 'randomstuff'},
    ]
    res = matcher.match(cands, 'resume')
    names = [r['name'] for r in res]
    assert 'Python' in names
    ml_entry = next(r for r in res if r['name'] == 'Machine Learning')
    assert ml_entry['confidence'] == 1.0
    assert ml_entry['evidence']['start'] == '2021-01'
    dl_entry = next(r for r in res if r['name'] == 'Deep Learning')
    assert 0.72 <= dl_entry['confidence'] <= 1.0
    assert all(r['evidence']['snippet'] != 'randomstuff' for r in res)

