import math
from datetime import datetime
from typing import Any, Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


def job_skill_weights(posting_text: str, required: List[str], preferred: List[str]) -> Dict[str, float]:
    skills = list(dict.fromkeys(required + preferred))
    if not skills:
        return {}
    vect = TfidfVectorizer(vocabulary=[s.lower() for s in skills])
    tfidf = vect.fit_transform([posting_text.lower()]).toarray()[0]
    weights = {skill: tfidf[i] for i, skill in enumerate(skills)}
    for skill in required:
        weights[skill] = weights.get(skill, 0) + 0.4
    for skill in preferred:
        weights[skill] = weights.get(skill, 0) + 0.15
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def resume_skill_weights(instances: List[Dict[str, Any]], lambda_: float = 0.03) -> Tuple[Dict[str, float], Dict[str, Any]]:
    weights: Dict[str, float] = {}
    evidence: Dict[str, Any] = {}
    now = datetime.utcnow()
    for inst in instances:
        skill = inst["name"]
        start = inst.get("start")
        end = inst.get("end") or start
        months_since = 6
        if end:
            end_dt = datetime.strptime(end, "%Y-%m")
            months_since = (now.year - end_dt.year) * 12 + (now.month - end_dt.month)
        tenure_months = 0
        if start and end:
            start_dt = datetime.strptime(start, "%Y-%m")
            end_dt = datetime.strptime(end, "%Y-%m")
            tenure_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
        tenure_years = tenure_months / 12.0
        decay = math.exp(-lambda_ * months_since)
        weight = tenure_years * decay
        weights[skill] = weights.get(skill, 0) + weight
        evidence[skill] = {
            "tenure_years": tenure_years,
            "months_since_last_use": months_since,
        }
    norm = math.sqrt(sum(v * v for v in weights.values())) or 1.0
    weights = {k: v / norm for k, v in weights.items()}
    return weights, evidence


def build_vectors(posting_text: str, required: List[str], preferred: List[str], resume_instances: List[Dict[str, Any]], lambda_: float = 0.03):
    job = job_skill_weights(posting_text, required, preferred)
    resume, evidence = resume_skill_weights(resume_instances, lambda_)
    return job, resume, evidence

