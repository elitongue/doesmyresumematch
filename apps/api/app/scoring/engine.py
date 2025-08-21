import math
from typing import Dict, List, Tuple, Any


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in keys))
    nb = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in keys))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def score_pair(
    resume_vector: Dict[str, float],
    job_vector: Dict[str, float],
    required_skills: List[str],
    level_gap: float,
    cluster_map: Dict[str, Dict[str, Any]],
    *,
    delta: float = 0.35,
    eta: float = 0.15,
    eps: float = 0.05,
) -> Tuple[float, Dict[str, float]]:
    """Score resume vs. job description.

    Returns a tuple of (score 0-100, terms used).
    """

    base = _cosine(resume_vector, job_vector)

    total_req = sum(job_vector.get(s, 0.0) for s in required_skills) or 1.0
    missing = sum(job_vector.get(s, 0.0) for s in required_skills if resume_vector.get(s, 0.0) == 0.0)
    pcrit = missing / total_req

    cluster_pen = 0.0
    for cl in cluster_map.values():
        r_vec = cl.get("resume", {})
        j_vec = cl.get("job", {})
        weight = cl.get("weight", 0.0)
        gap = 1.0 - _cosine(r_vec, j_vec)
        cluster_pen += weight * gap

    level_pen = abs(level_gap)

    score = base - delta * pcrit - eta * cluster_pen - eps * level_pen
    score = max(0.0, min(1.0, score)) * 100.0

    terms = {
        "base": base,
        "pcrit": pcrit,
        "cluster_penalty": cluster_pen,
        "level_penalty": eps * level_pen,
    }
    return score, terms
