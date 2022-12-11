"""alter manuscripts add fk series_id

Revision ID: 2771db46458a
Revises: 649d7956d21d
Create Date: 2022-12-10 19:10:53.462572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2771db46458a'
down_revision = '649d7956d21d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE manuscripts
ADD CONSTRAINT fk_series
FOREIGN KEY (series_id)
REFERENCES series (series_id)
ON DELETE RESTRICT;
""")


def downgrade():
    op.execute("""
ALTER TABLE manuscripts
DROP CONSTRAINT fk_series;
""")
