"""add index on books hash series_id

Revision ID: 0b893ceafe67
Revises: d6c50ee4f065
Create Date: 2022-12-11 11:53:54.001230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b893ceafe67'
down_revision = 'd6c50ee4f065'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE INDEX idx_books_series_id ON books USING hash(series_id);
""")


def downgrade():
    op.execute("""
DROP INDEX idx_books_series_id;
""")
