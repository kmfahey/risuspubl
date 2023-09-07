"""alter clients add fk salesperson_id

Revision ID: 6e9d47cf2b9e
Revises: 2771db46458a
Create Date: 2022-12-10 19:11:57.991932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6e9d47cf2b9e"
down_revision = "2771db46458a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE clients
ADD CONSTRAINT fk_salesperson
FOREIGN KEY (salesperson_id)
REFERENCES salespeople (salesperson_id)
ON DELETE RESTRICT;
"""
    )


def downgrade():
    op.execute(
        """
ALTER TABLE clients
DROP CONSTRAINT fk_salesperson;
"""
    )
