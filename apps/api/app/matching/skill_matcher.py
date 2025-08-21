import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from ..embeddings import provider


class SkillMatcher:
    def __init__(self, embedding_fn=provider.get_embedding):
        data = yaml.safe_load((Path(__file__).resolve().parents[1] / "taxonomy" / "skills.yaml").read_text())
        self.skills: List[Dict[str, Any]] = []
        self.alias_map: Dict[str, int] = {}
        sid = 1
        for items in data.values():
            for item in items:
                name = item["name"]
                self.skills.append({"id": sid, "name": name})
                self.alias_map[name.lower()] = sid
                for alias in item.get("aliases", []):
                    self.alias_map[alias.lower()] = sid
                sid += 1
        self._embeddings: Dict[int, List[float]] = {}
        self.embedding_fn = embedding_fn

    def _skill_embedding(self, skill_id: int) -> List[float]:
        if skill_id not in self._embeddings:
            name = next(s["name"] for s in self.skills if s["id"] == skill_id)
            self._embeddings[skill_id] = self.embedding_fn(name)
        return self._embeddings[skill_id]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def match(self, candidates: Iterable[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for cand in candidates:
            text = cand.get("text", "").strip()
            norm = text.lower()
            skill_id = self.alias_map.get(norm)
            confidence = 1.0
            if skill_id is None:
                emb = self.embedding_fn(norm)
                best_id = None
                best_sim = 0.0
                for s in self.skills:
                    se = self._skill_embedding(s["id"])
                    sim = self._cosine(emb, se)
                    if sim > best_sim:
                        best_sim = sim
                        best_id = s["id"]
                if best_id is None or best_sim < 0.72:
                    continue
                skill_id = best_id
                confidence = best_sim
            name = next(s["name"] for s in self.skills if s["id"] == skill_id)
            evidence = {"snippet": cand.get("snippet", text)}
            if cand.get("start") or cand.get("end"):
                evidence["start"] = cand.get("start")
                evidence["end"] = cand.get("end")
            results.append(
                {
                    "skill_id": skill_id,
                    "name": name,
                    "source": source,
                    "confidence": confidence,
                    "evidence": evidence,
                }
            )
        return results

