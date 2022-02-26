"""Rename User to Member

Revision ID: 89fac7c8d13a
Revises: 23ea1b4faa2c
Create Date: 2022-02-18 16:24:15.664137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89fac7c8d13a'
down_revision = '23ea1b4faa2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('user', 'team_member')
    op.execute('ALTER SEQUENCE  user_id_seq RENAME TO team_member_id_seq')
    op.execute('ALTER INDEX user_pkey RENAME TO team_member_pkey')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.alter_column('reminder', 'user_id', new_column_name='team_member_id')
    op.alter_column('participants', 'user_id', nullable=False, new_column_name='team_member_id')
    op.alter_column('feedback_tag_group', 'user_id', new_column_name='team_member_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('team_member', 'user')
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.execute('ALTER SEQUENCE  team_member_id_seq RENAME TO user_id_seq')
    op.execute('ALTER INDEX team_member_pkey RENAME TO user_pkey')
    op.alter_column('reminder', 'team_member_id', new_column_name='user_id')
    op.alter_column('participants', 'team_member_id', new_column_name='user_id')
    op.alter_column('feedback_tag_group', 'team_member_id', new_column_name='user_id')
    # ### end Alembic commands ###
