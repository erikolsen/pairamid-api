"""add pair history

Revision ID: 0cc8a9b4e812
Revises: 4faaf976e4b9
Create Date: 2020-04-01 06:24:52.405434

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0cc8a9b4e812'
down_revision = '4faaf976e4b9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pair_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pairs', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('pair_history')
