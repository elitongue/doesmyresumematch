import hashlib
import json
from typing import List

from sqlalchemy import Column, Integer, String, Text, select

from ..db import Base, get_engine, get_session
from .provider import get_embedding


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True)
    text_hash = Column(String, unique=True, index=True, nullable=False)
    embedding = Column(Text, nullable=False)


def chunk_text(text: str, max_tokens: int = 700) -> List[str]:
    tokens = text.split()
    chunks = [" ".join(tokens[i : i + max_tokens]) for i in range(0, len(tokens), max_tokens)]
    return chunks or [""]


def embed_text(text: str, engine=None) -> List[List[float]]:
    engine = engine or get_engine()
    Base.metadata.create_all(bind=engine)
    session = get_session(engine)

    results: List[List[float]] = []
    for chunk in chunk_text(text):
        digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        record = session.execute(select(Embedding).where(Embedding.text_hash == digest)).scalar_one_or_none()
        if record:
            results.append(json.loads(record.embedding))
            continue
        emb = get_embedding(chunk)
        session.add(Embedding(text_hash=digest, embedding=json.dumps(emb)))
        session.commit()
        results.append(emb)
    session.close()
    return results
