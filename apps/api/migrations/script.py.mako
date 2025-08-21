"""${message}

Revision ID: ${revision}
Revises: ${down_revision | default('None')}
Create Date: ${create_date}
"""

from alembic import op
import sqlalchemy as sa
${imports if imports}

def upgrade() -> None:
    ${upgrades if upgrades else 'pass'}

def downgrade() -> None:
    ${downgrades if downgrades else 'pass'}
