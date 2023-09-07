"""create salespeople

Revision ID: 6b2da27f9ce8
Revises: b789abda0fbb
Create Date: 2022-12-10 18:33:18.219322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b2da27f9ce8"
down_revision = "b789abda0fbb"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE TABLE salespeople (
    salesperson_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    salary NUMERIC NOT NULL
);
"""
    )


def downgrade():
    op.execute(
        """
DROP TABLE salespeople;
"""
    )
