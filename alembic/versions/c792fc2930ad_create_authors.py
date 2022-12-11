"""create authors

Revision ID: c792fc2930ad
Revises: 
Create Date: 2022-12-10 18:25:28.563828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c792fc2930ad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE authors;
""")
