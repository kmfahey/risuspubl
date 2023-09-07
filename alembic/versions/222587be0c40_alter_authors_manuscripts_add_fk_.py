"""alter authors_manuscripts add fk manuscript_id

Revision ID: 222587be0c40
Revises: a040fd3c0003
Create Date: 2022-12-10 18:48:53.574679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "222587be0c40"
down_revision = "a040fd3c0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE authors_manuscripts
ADD CONSTRAINT fk_manuscripts
FOREIGN KEY (manuscript_id)
REFERENCES manuscripts (manuscript_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE authors_manuscripts
DROP CONSTRAINT fk_manuscripts;
"""
    )
