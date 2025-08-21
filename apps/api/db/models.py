import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    consent_save = sa.Column(sa.Boolean, server_default=sa.text("false"), nullable=False)

    documents = relationship("Document", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)
    user_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=True)
    kind = sa.Column(sa.Enum("resume", "job", name="document_kind"), index=True, nullable=False)
    raw_text = sa.Column(sa.Text, nullable=False)
    source_file_name = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)

    user = relationship("User", back_populates="documents")
    embeddings = relationship("Embedding", back_populates="document")
    extracted_skills = relationship("ExtractedSkill", back_populates="document")


class Skill(Base):
    __tablename__ = "skills"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    cluster = sa.Column(sa.Text, nullable=True)
    is_canonical = sa.Column(sa.Boolean, server_default=sa.text("true"), nullable=False)

    aliases = relationship("SkillAlias", back_populates="canonical_skill")
    extracted_skills = relationship("ExtractedSkill", back_populates="skill")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = sa.Column(sa.Integer, primary_key=True)
    alias = sa.Column(sa.Text, unique=True, nullable=False)
    canonical_skill_id = sa.Column(sa.Integer, sa.ForeignKey("skills.id"), index=True, nullable=False)

    canonical_skill = relationship("Skill", back_populates="aliases")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)
    doc_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), index=True, nullable=False)
    chunk_index = sa.Column(sa.Integer, nullable=False)
    vector = sa.Column(Vector(1536), nullable=False)
    text_span = sa.Column(sa.Text, nullable=True)

    document = relationship("Document", back_populates="embeddings")

    __table_args__ = (
        sa.UniqueConstraint("doc_id", "chunk_index", name="uq_embeddings_doc_chunk"),
    )


class ExtractedSkill(Base):
    __tablename__ = "extracted_skills"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)
    doc_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), index=True, nullable=False)
    skill_id = sa.Column(sa.Integer, sa.ForeignKey("skills.id"), index=True, nullable=False)
    confidence = sa.Column(sa.Float, nullable=False)
    recency_months = sa.Column(sa.Integer, nullable=True)
    evidence = sa.Column(pg.JSONB, nullable=True)

    document = relationship("Document", back_populates="extracted_skills")
    skill = relationship("Skill", back_populates="extracted_skills")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)
    resume_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), index=True, nullable=False)
    job_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), index=True, nullable=False)
    score = sa.Column(sa.Float, nullable=False)
    label = sa.Column(sa.Text, nullable=True)
    details = sa.Column(pg.JSONB, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)

    __table_args__ = (
        sa.Index("ix_match_results_resume_job", "resume_id", "job_id"),
    )
