"""alter manuscripts add fk editor_id

Revision ID: 649d7956d21d
Revises: 9a6436d16a31
Create Date: 2022-12-10 19:08:38.590855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '649d7956d21d'
down_revision = '9a6436d16a31'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE manuscripts
ADD CONSTRAINT fk_editors
FOREIGN KEY (editor_id)
REFERENCES editors (editor_id)
ON DELETE RESTRICT;
""")


def downgrade():
    op.execute("""
ALTER TABLE manuscripts
DROP CONSTRAINT fk_editors;
""")
