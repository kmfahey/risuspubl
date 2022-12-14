"""create manuscripts

Revision ID: a5f63a8a4776
Revises: 336d82ae5191
Create Date: 2022-12-10 18:29:23.530832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5f63a8a4776'
down_revision = '336d82ae5191'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE manuscripts (
    manuscript_id SERIAL PRIMARY KEY,
    editor_id INT,
    series_id INT,
    working_title VARCHAR(64) UNIQUE NOT NULL,
    due_date DATE NOT NULL,
    advance NUMERIC NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE manuscripts;
""")
