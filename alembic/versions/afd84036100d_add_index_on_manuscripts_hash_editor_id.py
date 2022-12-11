"""add index on manuscripts hash editor_id

Revision ID: afd84036100d
Revises: c50853de2e55
Create Date: 2022-12-11 11:55:56.667249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afd84036100d'
down_revision = 'c50853de2e55'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE INDEX idx_manuscripts_editor_id ON manuscripts USING hash(editor_id);
""")


def downgrade():
    op.execute("""
DROP INDEX idx_manuscripts_editor_id;
""")
