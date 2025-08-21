#!/usr/bin/env python
import argparse
import csv
import json
import math
import re
from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ensure app package can be imported
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.parsing.job_parser import parse_job
from app.scoring import engine, vectors

LABELS = ["reject", "stretch", "on_target", "strong"]
DEFAULT_THRESHOLDS = [25, 50, 75]
DEFAULT_PARAMS = {"delta": 0.35, "eta": 0.15, "eps": 0.05, "lambda": 0.03}
PARAM_GRID = {
    "delta": [0.25, 0.35, 0.45],
    "eta": [0.1, 0.15, 0.2],
    "eps": [0.03, 0.05, 0.07],
    "lambda": [0.01, 0.03, 0.05],
}


def _load_skill_clusters() -> Dict[str, str]:
    data_path = ROOT / "app" / "taxonomy" / "skills.yaml"
    mapping: Dict[str, str] = {}
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


def _parse_resume_text(text: str) -> List[Dict[str, Any]]:
    tokens = [t.strip() for t in re.split(r"[\n,;]", text) if t.strip()]
    instances = [
        {"name": token, "start": "2020-01", "end": "2024-01"}
        for token in tokens
    ]
    return instances


def _classify(score: float) -> str:
    if score < DEFAULT_THRESHOLDS[0]:
        return "reject"
    if score < DEFAULT_THRESHOLDS[1]:
        return "stretch"
    if score < DEFAULT_THRESHOLDS[2]:
        return "on_target"
    return "strong"


def _score_example(
    resume_text: str,
    job_text: str,
    *,
    delta: float,
    eta: float,
    eps: float,
    lambda_: float,
) -> float:
    job = parse_job(job_text)
    resume_instances = _parse_resume_text(resume_text)
    posting_text = job.get("title", "") + "\n" + "\n".join(
        job.get("responsibilities", [])
        + job.get("required_skills", [])
        + job.get("preferred_skills", [])
    )
    job_vec = vectors.job_skill_weights(
        posting_text, job.get("required_skills", []), job.get("preferred_skills", [])
    )
    resume_vec, _ = vectors.resume_skill_weights(resume_instances, lambda_)
    clusters = _cluster_map(job_vec, resume_vec)
    score, _ = engine.score_pair(
        resume_vec,
        job_vec,
        job.get("required_skills", []),
        0.0,
        clusters,
        delta=delta,
        eta=eta,
        eps=eps,
    )
    return score


def evaluate(rows: List[Dict[str, str]], params: Dict[str, float]):
    scores = []
    preds = []
    truth = []
    for r in rows:
        score = _score_example(
            r["resume_text"],
            r["job_text"],
            delta=params["delta"],
            eta=params["eta"],
            eps=params["eps"],
            lambda_=params["lambda"],
        )
        scores.append(score)
        preds.append(_classify(score))
        truth.append(r["human_label"])
    acc = accuracy_score(truth, preds)
    cm = confusion_matrix(truth, preds, labels=LABELS)
    report = classification_report(truth, preds, labels=LABELS)
    return acc, cm, report


def grid_search(rows: List[Dict[str, str]]):
    best_params = None
    best_acc = -math.inf
    for delta, eta, eps, lam in product(
        PARAM_GRID["delta"],
        PARAM_GRID["eta"],
        PARAM_GRID["eps"],
        PARAM_GRID["lambda"],
    ):
        params = {"delta": delta, "eta": eta, "eps": eps, "lambda": lam}
        acc, _, _ = evaluate(rows, params)
        if acc > best_acc:
            best_acc = acc
            best_params = params
    return best_params, best_acc


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate scoring parameters")
    parser.add_argument("csv", help="Path to labeled pairs CSV")
    args = parser.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print("Evaluating default parameters...")
    acc, cm, report = evaluate(rows, DEFAULT_PARAMS)
    print(f"Accuracy: {acc:.3f}")
    print("Confusion matrix (rows=truth, cols=pred):")
    print(cm)
    print(report)

    print("Searching parameter grid...")
    best_params, best_acc = grid_search(rows)
    print("Best params:", best_params)
    print(f"Best accuracy: {best_acc:.3f}")

    params_path = ROOT / "app" / "scoring" / "params.json"
    params_path.write_text(json.dumps(best_params, indent=2))
    print(f"Wrote best parameters to {params_path}")


if __name__ == "__main__":
    main()
