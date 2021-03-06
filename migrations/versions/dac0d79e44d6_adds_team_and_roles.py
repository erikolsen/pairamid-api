"""Adds team and roles

Revision ID: dac0d79e44d6
Revises: 4faaf976e4b9
Create Date: 2020-05-14 13:06:29.678042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dac0d79e44d6'
down_revision = '4faaf976e4b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('color', sa.String(length=64), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pairing_session_uuid'), 'pairing_session', ['uuid'], unique=False)
    op.add_column('user', sa.Column('first_name', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('role_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_user_uuid'), 'user', ['uuid'], unique=False)
    op.create_foreign_key(None, 'user', 'team', ['team_id'], ['id'])
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    op.drop_column('user', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_index(op.f('ix_user_uuid'), table_name='user')
    op.drop_column('user', 'team_id')
    op.drop_column('user', 'role_id')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    op.drop_index(op.f('ix_pairing_session_uuid'), table_name='pairing_session')
    op.drop_table('role')
    op.drop_table('team')
    # ### end Alembic commands ###
