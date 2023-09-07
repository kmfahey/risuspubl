"""create authors_manuscripts

Revision ID: 388dfda0ace7
Revises: 2190414d9eab
Create Date: 2022-12-10 18:27:34.207929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "388dfda0ace7"
down_revision = "2190414d9eab"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE TABLE authors_manuscripts (
    author_id INT,
    manuscript_id INT,
    PRIMARY KEY (author_id, manuscript_id)
);
"""
    )


def downgrade():
    op.execute(
        """
DROP TABLE authors_manuscripts;
"""
    )
