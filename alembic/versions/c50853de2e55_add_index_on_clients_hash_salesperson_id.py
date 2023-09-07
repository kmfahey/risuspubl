"""add index on clients hash salesperson_id

Revision ID: c50853de2e55
Revises: 0b893ceafe67
Create Date: 2022-12-11 11:55:06.651962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c50853de2e55"
down_revision = "0b893ceafe67"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE INDEX idx_clients_salesperson_id ON clients USING hash(salesperson_id);
"""
    )


def downgrade():
    op.execute(
        """
DROP INDEX idx_clients_salesperson_id;
"""
    )
