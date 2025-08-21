from typing import Any, Dict, List, Tuple


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sum(a.get(k, 0.0) ** 2 for k in keys) ** 0.5
    nb = sum(b.get(k, 0.0) ** 2 for k in keys) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _label(score: float) -> str:
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "On target"
    if score >= 55:
        return "Stretch"
    return "Reach"


def build_explanation(
    job_vector: Dict[str, float],
    resume_vector: Dict[str, float],
    required_skills: List[str],
    engine_out: Tuple[float, Dict[str, float]],
    evidence: Dict[str, Any],
    cluster_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    score, terms = engine_out
    best_fit: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    for skill in set(job_vector) & set(resume_vector):
        contrib = job_vector[skill] * resume_vector[skill]
        best_fit.append({
            "skill": skill,
            "contribution": contrib,
            "evidence": evidence.get(skill, {}),
        })
    best_fit.sort(key=lambda x: x["contribution"], reverse=True)
    best_fit = best_fit[:5]

    missing_required = [s for s in required_skills if resume_vector.get(s, 0.0) == 0.0]
    missing_required.sort(key=lambda s: job_vector.get(s, 0.0), reverse=True)
    for s in missing_required:
        gaps.append({"skill": s, "required": True})
    if len(gaps) < 5:
        others = [s for s in job_vector if resume_vector.get(s, 0.0) == 0.0 and s not in missing_required]
        others.sort(key=lambda s: job_vector.get(s, 0.0), reverse=True)
        for s in others:
            gaps.append({"skill": s, "required": False})
            if len(gaps) == 5:
                break

    clusters: List[Dict[str, Any]] = []
    for name, cl in cluster_map.items():
        align = _cosine(cl.get("resume", {}), cl.get("job", {}))
        r_vec = cl.get("resume", {})
        j_vec = cl.get("job", {})
        shared = set(r_vec) & set(j_vec)
        examples = sorted(shared, key=lambda s: j_vec[s] * r_vec[s], reverse=True)
        examples = examples[:3]
        gap_skills = [s for s in j_vec if s not in r_vec]
        gap_skills.sort(key=lambda s: j_vec[s], reverse=True)
        clusters.append(
            {
                "cluster": name,
                "align_pct": max(0.0, align) * 100.0,
                "best_examples": examples,
                "gaps": gap_skills[:3],
            }
        )

    return {
        "score": score,
        "label": _label(score),
        "best_fit": best_fit,
        "gaps": gaps,
        "clusters": clusters,
        "terms": terms,
    }
