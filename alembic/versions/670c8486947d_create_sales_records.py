"""create sales_records

Revision ID: 670c8486947d
Revises: 6b2da27f9ce8
Create Date: 2022-12-10 18:34:06.264687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '670c8486947d'
down_revision = '6b2da27f9ce8'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE sales_records (
    sales_record_id SERIAL PRIMARY KEY,
    book_id INT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    copies_sold INTEGER,
    gross_profit NUMERIC,
    net_profit NUMERIC
);
""")


def downgrade():
    op.execute("""
DROP TABLE sales_records;
""")
