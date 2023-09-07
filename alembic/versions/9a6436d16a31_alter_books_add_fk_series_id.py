"""alter books add fk series_id

Revision ID: 9a6436d16a31
Revises: c8f0f086f0a8
Create Date: 2022-12-10 18:53:51.590757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9a6436d16a31"
down_revision = "c8f0f086f0a8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE books
ADD CONSTRAINT fk_series
FOREIGN KEY (series_id)
REFERENCES series (series_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE books
DROP CONSTRAINT fk_series;
"""
    )
