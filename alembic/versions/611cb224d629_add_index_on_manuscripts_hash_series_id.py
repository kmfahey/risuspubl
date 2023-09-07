"""add index on manuscripts hash series_id

Revision ID: 611cb224d629
Revises: afd84036100d
Create Date: 2022-12-11 11:56:43.534425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "611cb224d629"
down_revision = "afd84036100d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE INDEX idx_manuscripts_series_id ON manuscripts USING hash(series_id);
"""
    )


def downgrade():
    op.execute(
        """
DROP INDEX idx_manuscripts_series_id;
"""
    )
