from typing import Any, Dict, List

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    doc_id: int
    data: Dict[str, Any]


class ParseJobRequest(BaseModel):
    source: str


class MatchRequest(BaseModel):
    resume_doc_id: int
    job_doc_id: int


class MatchResponse(BaseModel):
    score: float
    label: str
    best_fit: List[Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    clusters: List[Dict[str, Any]]
    terms: Dict[str, float]
