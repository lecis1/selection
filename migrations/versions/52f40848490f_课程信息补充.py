"""'课程信息补充'

Revision ID: 52f40848490f
Revises: c44e46438aa7
Create Date: 2020-11-28 15:01:44.790250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52f40848490f'
down_revision = 'c44e46438aa7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('academic_year', sa.String(length=64), nullable=True))
    op.add_column('courses', sa.Column('begin_college', sa.String(length=64), nullable=True))
    op.add_column('courses', sa.Column('course_category', sa.String(length=64), nullable=True))
    op.add_column('courses', sa.Column('credit_hour', sa.Float(precision=6), nullable=True))
    op.add_column('courses', sa.Column('semester', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'semester')
    op.drop_column('courses', 'credit_hour')
    op.drop_column('courses', 'course_category')
    op.drop_column('courses', 'begin_college')
    op.drop_column('courses', 'academic_year')
    # ### end Alembic commands ###
