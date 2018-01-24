"""version 1.5.2

Revision ID: 56608def7269
Revises: eb7141efd75a
Create Date: 2016-08-17 09:19:59.008773

"""

# revision identifiers, used by Alembic.
revision = '56608def7269'
down_revision = 'f75b4068af0a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('irma_file', 'size',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)

def downgrade():
    op.alter_column('irma_file', 'size',
                    nullable=False,
                    type_=sa.Integer(),
                    existing_type=sa.BigInteger(),
                    existing_server_default=False)
