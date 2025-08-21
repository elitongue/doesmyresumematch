FROM python:3.11-slim AS builder

WORKDIR /app
COPY apps/api/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt gunicorn

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY apps/api /app
EXPOSE 8000
CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker -w $((2 * $(nproc))) -b 0.0.0.0:8000"]
