"""Adds feedback tables

Revision ID: c3f746489f19
Revises: 3a8d6da48365
Create Date: 2021-03-12 21:03:33.053193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f746489f19'
down_revision = '3a8d6da48365'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('sender_name', sa.String(length=64), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feedback_tag_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feedback_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['feedback_tag_group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tagged_feedback',
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.Column('feedback_tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.id'], ),
    sa.ForeignKeyConstraint(['feedback_tag_id'], ['feedback_tag.id'], ),
    sa.PrimaryKeyConstraint('feedback_id', 'feedback_tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tagged_feedback')
    op.drop_table('feedback_tag')
    op.drop_table('feedback_tag_group')
    op.drop_table('feedback')
    # ### end Alembic commands ###
