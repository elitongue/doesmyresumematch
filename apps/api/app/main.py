import itertools
import logging
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml
from fastapi import Body, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .llm.rewrites import get_model_usage, suggest_rewrites
from .parsing.job_parser import parse_job
from .parsing.resume_parser import parse_resume
from .schemas import DocumentResponse, MatchRequest, MatchResponse, ParseJobRequest
from .scoring import engine, explain, vectors

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.state.settings = settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_RESUMES: Dict[int, Dict[str, Any]] = {}
_JOBS: Dict[int, Dict[str, Any]] = {}
_MATCHES: Dict[int, Dict[str, Any]] = {}
_DOC_OWNERS: Dict[int, str] = {}
_counter = itertools.count(1)

# load taxonomy mapping
_SKILL_CLUSTER: Dict[str, str] = {}
_data_path = Path(__file__).resolve().parent / "taxonomy" / "skills.yaml"
if _data_path.exists():
    data = yaml.safe_load(_data_path.read_text())
    for cluster, skills in data.items():
        for item in skills:
            name = item["name"].lower()
            _SKILL_CLUSTER[name] = cluster
            for alias in item.get("aliases", []):
                _SKILL_CLUSTER[alias.lower()] = cluster


def _cluster_map(job_vec: Dict[str, float], resume_vec: Dict[str, float]):
    clusters: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"job": {}, "resume": {}, "weight": 0.0}
    )
    for skill, w in job_vec.items():
        cl = _SKILL_CLUSTER.get(skill.lower(), "Other")
        clusters[cl]["job"][skill] = w
        clusters[cl]["weight"] += w
    for skill, w in resume_vec.items():
        cl = _SKILL_CLUSTER.get(skill.lower(), "Other")
        clusters[cl]["resume"][skill] = w
    total = sum(job_vec.values()) or 1.0
    for c in clusters.values():
        c["weight"] = c["weight"] / total
    return clusters


def _score_bucket(score: float) -> str:
    if score < 0.25:
        return "0-0.25"
    if score < 0.5:
        return "0.25-0.5"
    if score < 0.75:
        return "0.5-0.75"
    return "0.75-1.0"


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/v1/parse/resume", response_model=DocumentResponse)
async def parse_resume_ep(
    data: bytes = Body(...), x_client_id: str = Header(..., alias="X-Client-Id")
):
    if len(data) > 2_000_000:
        raise HTTPException(status_code=400, detail="File too large")
    try:
        parsed = parse_resume(data, "resume.pdf")
    except Exception as e:  # pragma: no cover - defensive
        logger.exception("resume parse failed")
        raise HTTPException(status_code=400, detail=str(e))
    doc_id = next(_counter)
    _RESUMES[doc_id] = parsed
    _DOC_OWNERS[doc_id] = x_client_id
    return {"doc_id": doc_id, "data": parsed}


@app.post("/v1/parse/job", response_model=DocumentResponse)
async def parse_job_ep(
    req: ParseJobRequest, x_client_id: str = Header(..., alias="X-Client-Id")
):
    if len(req.source) > 1_000_000:
        raise HTTPException(status_code=400, detail="Input too large")
    try:
        parsed = parse_job(req.source)
    except Exception as e:  # pragma: no cover - defensive
        logger.exception("job parse failed")
        raise HTTPException(status_code=400, detail=str(e))
    doc_id = next(_counter)
    _JOBS[doc_id] = parsed
    _DOC_OWNERS[doc_id] = x_client_id
    return {"doc_id": doc_id, "data": parsed}


def _schedule_delete(doc_ids: Iterable[int]) -> None:
    def _worker():
        time.sleep(600)
        for doc_id in doc_ids:
            _RESUMES.pop(doc_id, None)
            _JOBS.pop(doc_id, None)
            _MATCHES.pop(doc_id, None)
            _DOC_OWNERS.pop(doc_id, None)

    threading.Thread(target=_worker, daemon=True).start()


@app.post("/v1/match", response_model=MatchResponse)
async def match_ep(
    req: MatchRequest,
    x_client_id: str = Header(..., alias="X-Client-Id"),
    consent_save: bool = Header(False, alias="X-Consent-Save"),
):
    start = time.time()
    if settings.analytics_enabled:
        logger.info("match_requested")
    resume = _RESUMES.get(req.resume_doc_id)
    job = _JOBS.get(req.job_doc_id)
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Documents not found")

    resume_instances = [{"name": s} for s in resume.get("skills", [])]
    posting_text = (
        job.get("title", "")
        + "\n"
        + "\n".join(
            job.get("responsibilities", [])
            + job.get("required_skills", [])
            + job.get("preferred_skills", [])
        )
    )
    job_vec, resume_vec, evidence = vectors.build_vectors(
        posting_text,
        job.get("required_skills", []),
        job.get("preferred_skills", []),
        resume_instances,
    )
    clusters = _cluster_map(job_vec, resume_vec)
    score, terms = engine.score_pair(
        resume_vec, job_vec, job.get("required_skills", []), 0.0, clusters
    )
    explanation = explain.build_explanation(
        job_vec,
        resume_vec,
        job.get("required_skills", []),
        (score, terms),
        evidence,
        clusters,
    )
    bullets = []
    rewrites = suggest_rewrites(
        bullets, [g["skill"] for g in explanation.get("gaps", [])]
    )
    explanation["rewrites"] = rewrites
    doc_id = next(_counter)
    _MATCHES[doc_id] = explanation
    _DOC_OWNERS[doc_id] = x_client_id
    if not consent_save:
        _schedule_delete([req.resume_doc_id, req.job_doc_id, doc_id])
    if settings.analytics_enabled:
        bucket = _score_bucket(score)
        duration = time.time() - start
        logger.info(
            "match_completed bucket=%s duration=%.2f model_usage=%s",
            bucket,
            duration,
            get_model_usage(),
        )
    return explanation


@app.delete("/v1/user/data")
async def delete_user_data(x_client_id: str = Header(..., alias="X-Client-Id")):
    for doc_id, owner in list(_DOC_OWNERS.items()):
        if owner == x_client_id:
            _RESUMES.pop(doc_id, None)
            _JOBS.pop(doc_id, None)
            _MATCHES.pop(doc_id, None)
            _DOC_OWNERS.pop(doc_id, None)
    return {"status": "deleted"}


@app.post("/v1/metrics")
async def metrics_ep(payload: Dict[str, Any]):
    if settings.analytics_enabled:
        event = payload.get("event")
        logger.info("metric event=%s", event)
    return {"status": "ok"}
