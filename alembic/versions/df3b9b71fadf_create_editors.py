"""create editors

Revision ID: df3b9b71fadf
Revises: 28db1c1066eb
Create Date: 2022-12-10 18:30:52.956007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df3b9b71fadf'
down_revision = '28db1c1066eb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE editors (
    editor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    salary NUMERIC NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE editors;
""")
