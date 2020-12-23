"""empty message

Revision ID: 8fdc441a7c32
Revises: 388ade63e4ae
Create Date: 2020-12-08 20:15:29.842351

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8fdc441a7c32'
down_revision = '388ade63e4ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('course_sid', sa.String(length=64), nullable=True))
    op.drop_index('course_sid', table_name='courses')
    op.create_unique_constraint(None, 'courses', ['course_sid'])
    op.drop_column('courses', 'course_sid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('course_sid', mysql.VARCHAR(length=64), nullable=True))
    op.drop_constraint(None, 'courses', type_='unique')
    op.create_index('course_sid', 'courses', ['course_sid'], unique=True)
    op.drop_column('courses', 'course_sid')
    # ### end Alembic commands ###
