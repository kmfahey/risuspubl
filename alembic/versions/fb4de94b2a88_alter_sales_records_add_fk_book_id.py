"""alter sales_records add fk book_id

Revision ID: fb4de94b2a88
Revises: 6e9d47cf2b9e
Create Date: 2022-12-10 19:37:54.327955

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb4de94b2a88'
down_revision = '6e9d47cf2b9e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE sales_records
ADD CONSTRAINT fk_book
FOREIGN KEY (book_id)
REFERENCES books (book_id)
ON DELETE RESTRICT;
""")


def downgrade():
    op.execute("""
ALTER TABLE sales_records
DROP CONSTRAINT fk_book;
""")
