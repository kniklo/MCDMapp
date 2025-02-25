"""Create Alternative and Criterion tables

Revision ID: b6a97c59f3e7
Revises: 
Create Date: 2025-01-30 11:12:41.100990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6a97c59f3e7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alternative',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('alternative', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_alternative_name'), ['name'], unique=True)

    op.create_table('criterion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('criterion', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_criterion_name'), ['name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('criterion', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_criterion_name'))

    op.drop_table('criterion')
    with op.batch_alter_table('alternative', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_alternative_name'))

    op.drop_table('alternative')
    # ### end Alembic commands ###
