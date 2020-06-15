"""Add uuid to Team

Revision ID: b57757d7a6f3
Revises: dac0d79e44d6
Create Date: 2020-05-23 21:43:53.047072

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b57757d7a6f3'
down_revision = 'dac0d79e44d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_team_uuid'), 'team', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_team_uuid'), table_name='team')
    op.drop_column('team', 'uuid')
    # ### end Alembic commands ###