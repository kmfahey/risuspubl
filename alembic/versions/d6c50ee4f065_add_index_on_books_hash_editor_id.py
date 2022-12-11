"""add index on books hash editor_id

Revision ID: d6c50ee4f065
Revises: fb4de94b2a88
Create Date: 2022-12-11 11:52:47.614425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6c50ee4f065'
down_revision = 'fb4de94b2a88'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE INDEX idx_books_editor_id ON books USING hash(editor_id);
""")


def downgrade():
    op.execute("""
DROP INDEX idx_books_editor_id;
""")
