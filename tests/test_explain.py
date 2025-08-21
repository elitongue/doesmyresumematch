from pathlib import Path
__import__('sys').path.insert(0, str(Path(__file__).resolve().parents[1] / 'apps/api'))

from app.scoring.explain import build_explanation  # noqa: E402

def _exp(score):
    job = {'Python': 0.6, 'SQL': 0.4}
    resume = {'Python': 0.6}
    required = ['Python', 'SQL']
    evidence = {}
    cluster = {'All': {'job': job, 'resume': resume, 'weight': 1.0}}
    return build_explanation(job, resume, required, (score, {}), evidence, cluster)

def test_label_boundaries():
    assert _exp(85)['label'] == 'Strong'
    assert _exp(70)['label'] == 'On target'
    assert _exp(55)['label'] == 'Stretch'
    assert _exp(54)['label'] == 'Reach'

def test_best_fit_and_gaps_ordering():
    job = {'Python': 0.6, 'SQL': 0.4}
    resume = {'Python': 0.6}
    required = ['Python', 'SQL']
    evidence = {}
    cluster = {'All': {'job': job, 'resume': resume, 'weight': 1.0}}
    out = build_explanation(job, resume, required, (90, {}), evidence, cluster)
    assert out['best_fit'][0]['skill'] == 'Python'
    gap_names = [g['skill'] for g in out['gaps']]
    assert gap_names[0] == 'SQL'
