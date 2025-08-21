#!/usr/bin/env python
"""CLI to run resume-job match scoring locally."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import yaml

# Ensure the app package can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.parsing.job_parser import parse_job  # noqa: E402
from app.parsing.resume_parser import parse_resume  # noqa: E402
from app.scoring import engine, explain, vectors  # noqa: E402


def _load_skill_clusters() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    data_path = ROOT / "app" / "taxonomy" / "skills.yaml"
    if data_path.exists():
        data = yaml.safe_load(data_path.read_text())
        for cluster, skills in data.items():
            for item in skills:
                name = item["name"].lower()
                mapping[name] = cluster
                for alias in item.get("aliases", []):
                    mapping[alias.lower()] = cluster
    return mapping


_SKILL_CLUSTER = _load_skill_clusters()


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


def run_pipeline(resume_path: str, job_source: str) -> Dict[str, Any]:
    resume_bytes = Path(resume_path).read_bytes()
    resume = parse_resume(resume_bytes, Path(resume_path).name)

    if job_source.startswith("http"):
        job_text = job_source
    else:
        job_text = Path(job_source).read_text(encoding="utf-8")
    job = parse_job(job_text)

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
    return explanation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run resume/job match locally")
    parser.add_argument("--resume", required=True, help="Path to resume file")
    parser.add_argument(
        "--job", required=True, help="Path to job description file or URL"
    )
    parser.add_argument("--json", required=True, help="Path to write output JSON")
    args = parser.parse_args()

    result = run_pipeline(args.resume, args.job)
    Path(args.json).write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
