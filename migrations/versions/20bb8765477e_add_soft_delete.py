"""Add soft delete

Revision ID: 20bb8765477e
Revises: 878c8eaf1ad3
Create Date: 2020-07-18 17:36:17.909029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20bb8765477e'
down_revision = '878c8eaf1ad3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pairing_session', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('participants', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('reminder', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'deleted')
    op.drop_column('reminder', 'deleted')
    op.drop_column('participants', 'deleted')
    op.drop_column('pairing_session', 'deleted')
    # ### end Alembic commands ###
