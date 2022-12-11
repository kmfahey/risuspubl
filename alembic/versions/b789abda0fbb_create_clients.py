"""create clients

Revision ID: b789abda0fbb
Revises: df3b9b71fadf
Create Date: 2022-12-10 18:32:38.229570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b789abda0fbb'
down_revision = 'df3b9b71fadf'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    salesperson_id INT NOT NULL,
    email_address VARCHAR(64) UNIQUE NOT NULL,
    phone_number VARCHAR(11) UNIQUE NOT NULL,
    business_name VARCHAR(64) UNIQUE NOT NULL,
    street_address VARCHAR(64) NOT NULL,
    city VARCHAR(64) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zipcode VARCHAR(9) NOT NULL,
    country VARCHAR(64) NOT NULL
);
""")


def downgrade():
    op.execute("""
DROP TABLE clients;
""")
