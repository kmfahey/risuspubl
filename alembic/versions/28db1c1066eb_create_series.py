"""create series

Revision ID: 28db1c1066eb
Revises: a5f63a8a4776
Create Date: 2022-12-10 18:30:12.031988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "28db1c1066eb"
down_revision = "a5f63a8a4776"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE TABLE series (
    series_id SERIAL PRIMARY KEY,
    title VARCHAR(64) UNIQUE NOT NULL,
    volumes INT NOT NULL
);
"""
    )


def downgrade():
    op.execute(
        """
DROP TABLE series;
"""
    )
