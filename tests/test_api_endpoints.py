import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))

os.environ.setdefault("DEV_MODE", "1")
os.environ.setdefault("ALLOW_ORIGINS", "http://localhost:3000")

from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / "apps/api/tests/fixtures"


def _load(name: str) -> bytes:
    return base64.b64decode((FIXTURES / name).read_text())


def test_endpoints_flow():
    client = TestClient(app)
    assert client.get("/healthz").status_code == 200

    data = _load("resume1_pdf.txt")
    res = client.post(
        "/v1/parse/resume",
        data=data,
        headers={"Content-Type": "application/pdf", "X-Client-Id": "test"},
    )
    resume_id = res.json()["doc_id"]

    job_text = "Engineer\nRequirements:\n- Python\nPreferred:\n- SQL"
    resj = client.post(
        "/v1/parse/job",
        json={"source": job_text},
        headers={"X-Client-Id": "test"},
    )
    job_id = resj.json()["doc_id"]

    match = client.post(
        "/v1/match",
        json={"resume_doc_id": resume_id, "job_doc_id": job_id},
        headers={"X-Client-Id": "test"},
    )
    body = match.json()
    assert "score" in body and "label" in body


def test_cors_preflight():
    client = TestClient(app)
    res = client.options(
        "/v1/parse/resume",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert res.status_code == 200
    assert (
        res.headers.get("access-control-allow-origin")
        == "http://localhost:3000"
    )
