"""create authors_metadata

Revision ID: fb0694e5e019
Revises: 66d37e1125cf
Create Date: 2022-12-11 13:20:21.250698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb0694e5e019"
down_revision = "66d37e1125cf"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE TABLE authors_metadata (
    author_metadata_id SERIAL PRIMARY KEY,
    author_id INT,
    age INT NOT NULL,
    biography TEXT NOT NULL,
    photo_url VARCHAR(256) NOT NULL,
    photo_res_horiz INT NOT NULL,
    photo_res_vert INT NOT NULL
);
"""
    )


def downgrade():
    op.execute(
        """
DROP TABLE authors_metadata;
"""
    )
