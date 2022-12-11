"""add index on sales_records hash book_id

Revision ID: 66d37e1125cf
Revises: 611cb224d629
Create Date: 2022-12-11 11:57:36.149710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66d37e1125cf'
down_revision = '611cb224d629'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE INDEX idx_sales_records_book_id ON sales_records USING hash(book_id);
""")


def downgrade():
    op.execute("""
DROP INDEX idx_sales_records_book_id;
""")
