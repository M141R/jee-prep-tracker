"""Add UserMockTest model

Revision ID: dab6dd21a797
Revises: 20a93d21271f
Create Date: 2025-02-19 05:06:17.593496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dab6dd21a797'
down_revision = '20a93d21271f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_mock_test',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('mock_test_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('total_marks', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['mock_test_id'], ['mock_test.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mock_test', schema=None) as batch_op:
        batch_op.drop_constraint('mock_test_user_id_fkey', type_='foreignkey')
        batch_op.drop_column('score')
        batch_op.drop_column('total_marks')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mock_test', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('total_marks', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('score', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('mock_test_user_id_fkey', 'user', ['user_id'], ['id'])

    op.drop_table('user_mock_test')
    # ### end Alembic commands ###
