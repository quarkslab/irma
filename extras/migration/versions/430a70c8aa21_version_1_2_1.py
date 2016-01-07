"""version 1.2.1

Revision ID: 430a70c8aa21
Revises: 2cc69d5c53eb
Create Date: 2015-07-06 16:34:44.422586

"""

# revision identifiers, used by Alembic.
revision = '430a70c8aa21'
down_revision = '2cc69d5c53eb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('irma_file',
                    'timestamp_first_scan',
                    nullable=False,
                    type_=sa.Numeric(asdecimal=False),
                    existing_type=sa.Float(precision=2),
                    existing_server_default=False,
                    existing_nullable=False)
    op.alter_column('irma_file',
                    'timestamp_last_scan',
                    nullable=False,
                    type_=sa.Numeric(asdecimal=False),
                    existing_type=sa.Float(precision=2),
                    existing_server_default=False,
                    existing_nullable=False)
    op.alter_column('irma_scanEvents',
                    'timestamp',
                    nullable=False,
                    type_=sa.Numeric(asdecimal=False),
                    existing_type=sa.Float(precision=2),
                    existing_server_default=False,
                    existing_nullable=False)


def downgrade():
    op.alter_column('irma_file',
                    'timestamp_first_scan',
                    nullable=False,
                    type_=sa.Float(precision=2),
                    existing_type=sa.Numeric(asdecimal=False),
                    existing_server_default=False,
                    existing_nullable=False)
    op.alter_column('irma_file',
                    'timestamp_last_scan',
                    nullable=False,
                    type_=sa.Float(precision=2),
                    existing_type=sa.Numeric(asdecimal=False),
                    existing_server_default=False,
                    existing_nullable=False)
    op.alter_column('irma_scanEvents',
                    'timestamp',
                    nullable=False,
                    type_=sa.Float(precision=2),
                    existing_type=sa.Numeric(asdecimal=False),
                    existing_server_default=False,
                    existing_nullable=False)
