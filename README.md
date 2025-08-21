# doesmyresumematch.com

**Upload your resume + a job posting → get a transparent match score with strengths & gaps.**

This project turns a skill-mismatch framework (cluster alignment, required-skill coverage, and seniority fit) into a simple, explainable score (0–100) plus actionable suggestions.

---

## What it does (MVP)

- **Match score (0–100)** with label: _Strong_, _On target_, _Stretch_, _Reach_
- **Breakdown**: best-fit skills & missing/weak skills (flags “required” gaps)
- **Cluster view**: alignment by high-level skill clusters (e.g., Data/ML, Programming, Communication)
- **Actionables**: grounded bullet rewrites (no fabrication)

## How it works (high level)

1. Parse resume (PDF/DOCX) and job text/URL into structured fields.
2. Map phrases → canonical skills (aliases + embeddings).
3. Build **job** weights (TF-IDF + required/preferred boosts) and **resume** weights (tenure × recency decay).
4. Score = cosine alignment − penalties for missing requireds, cluster gaps, seniority mismatch.
5. Return JSON with contributions, cluster bars, and suggested rewrites.

> Scoring sketch:  
> `Score = 100·cosine − 100·(δ·P_crit + η·P_cluster + ε·|level_gap|)`, then clipped to `[0,100]`.

## Tech stack (planned)

- **Frontend:** Next.js (App Router) + Tailwind
- **API:** FastAPI (Python)
- **Storage:** Postgres + pgvector (embeddings)
- **Models:** Text embeddings for matching; small LLM for parsing/rewrites (guarded)

## Quickstart

1. `cp .env.example .env` and fill in values
2. `docker compose up --build` → brings up DB, API, Web
3. Visit `http://localhost:3000` for the web UI

## Privacy ✱

- Default: no retention. Process in memory; delete docs right after scoring.
- Optional: user can opt-in to save results.
- Easy delete endpoint for client-id.

## Roadmap (MVP → v1)

- [ ] Repo scaffold (web, api, db, shared)
- [ ] Resume/job parsers
- [ ] Skill canonicalization + embedding matcher
- [ ] Vector weights (job/resume)
- [ ] Scoring engine + explanations
- [ ] Web UI (upload → results)
- [ ] PDF export, basic analytics (opt-in)
- [ ] Calibration script + params store
- [ ] Privacy controls & tests

## Dev notes

- Keep everything **explainable** (per-skill contributions & cluster bars).
- Guard LLM prompts to **never invent** user experience.
- Calibrate thresholds against a small labeled set.

## License

MIT — see `LICENSE`.
