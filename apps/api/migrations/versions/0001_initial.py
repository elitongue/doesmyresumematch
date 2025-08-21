"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2024-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("consent_save", sa.Boolean, server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("kind", sa.Enum("resume", "job", name="document_kind"), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("source_file_name", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_kind", "documents", ["kind"])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("cluster", sa.Text, nullable=True),
        sa.Column("is_canonical", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_skills_name", "skills", ["name"])

    op.create_table(
        "skill_aliases",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("alias", sa.Text, nullable=False),
        sa.Column("canonical_skill_id", sa.Integer, sa.ForeignKey("skills.id"), nullable=False),
        sa.UniqueConstraint("alias"),
    )
    op.create_index(
        "ix_skill_aliases_canonical_skill_id", "skill_aliases", ["canonical_skill_id"]
    )

    op.create_table(
        "embeddings",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("doc_id", pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("vector", Vector(1536), nullable=False),
        sa.Column("text_span", sa.Text, nullable=True),
        sa.UniqueConstraint("doc_id", "chunk_index", name="uq_embeddings_doc_chunk"),
    )
    op.create_index("ix_embeddings_doc_id", "embeddings", ["doc_id"])

    op.create_table(
        "extracted_skills",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("doc_id", pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("skill_id", sa.Integer, sa.ForeignKey("skills.id"), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("recency_months", sa.Integer, nullable=True),
        sa.Column("evidence", pg.JSONB, nullable=True),
    )
    op.create_index("ix_extracted_skills_doc_id", "extracted_skills", ["doc_id"])
    op.create_index("ix_extracted_skills_skill_id", "extracted_skills", ["skill_id"])

    op.create_table(
        "match_results",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("job_id", pg.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("label", sa.Text, nullable=True),
        sa.Column("details", pg.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_match_results_resume_id", "match_results", ["resume_id"])
    op.create_index("ix_match_results_job_id", "match_results", ["job_id"])
    op.create_index(
        "ix_match_results_resume_job", "match_results", ["resume_id", "job_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_match_results_resume_job", table_name="match_results")
    op.drop_index("ix_match_results_job_id", table_name="match_results")
    op.drop_index("ix_match_results_resume_id", table_name="match_results")
    op.drop_table("match_results")

    op.drop_index("ix_extracted_skills_skill_id", table_name="extracted_skills")
    op.drop_index("ix_extracted_skills_doc_id", table_name="extracted_skills")
    op.drop_table("extracted_skills")

    op.drop_index("ix_embeddings_doc_id", table_name="embeddings")
    op.drop_table("embeddings")

    op.drop_index(
        "ix_skill_aliases_canonical_skill_id", table_name="skill_aliases"
    )
    op.drop_table("skill_aliases")

    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")

    op.drop_index("ix_documents_kind", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")

    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS document_kind")
    op.execute("DROP EXTENSION IF EXISTS vector")
