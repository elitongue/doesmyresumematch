# Contributing

## Prerequisites
- Node.js 20+
- Python 3.11+
- Docker
- `pre-commit`

## Setup
```bash
npm install
pip install -r apps/api/requirements.txt
pre-commit install
```

## Run locally
### Web
```bash
npm --workspace apps/web run dev
```

### API
```bash
uvicorn apps.api.main:app --reload
```

## Run with Docker
```bash
docker compose up --build
```

## Format code
```bash
make fmt
```
