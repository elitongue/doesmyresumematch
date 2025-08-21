import os
import time
from typing import List

PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "openai").lower()


def _openai_embedding(text: str) -> List[float]:
    from openai import OpenAI, APIError, RateLimitError

    client = OpenAI()
    for attempt in range(3):
        try:
            resp = client.embeddings.create(model="text-embedding-3-small", input=text)
            return resp.data[0].embedding
        except (RateLimitError, APIError):
            time.sleep(2 ** attempt)
    raise RuntimeError("Failed to obtain embedding from OpenAI")


_local_model = None


def _local_embedding(text: str) -> List[float]:
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer

        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model.encode([text])[0].tolist()


def get_embedding(text: str) -> List[float]:
    if PROVIDER == "local":
        return _local_embedding(text)
    return _openai_embedding(text)
