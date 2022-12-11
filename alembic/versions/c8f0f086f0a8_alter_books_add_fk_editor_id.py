"""alter books add fk editor_id

Revision ID: c8f0f086f0a8
Revises: 222587be0c40
Create Date: 2022-12-10 18:52:57.211201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8f0f086f0a8'
down_revision = '222587be0c40'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE books
ADD CONSTRAINT fk_editors
FOREIGN KEY (editor_id)
REFERENCES editors (editor_id)
ON DELETE RESTRICT;
""")


def downgrade():
    op.execute("""
ALTER TABLE books
DROP CONSTRAINT fk_editors;
""")
