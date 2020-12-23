"""empty message

Revision ID: e6795a6f17b9
Revises: b9cec8294893
Create Date: 2020-11-29 20:36:54.647867

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e6795a6f17b9'
down_revision = 'b9cec8294893'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'test')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('test', mysql.VARCHAR(length=64), nullable=True))
    # ### end Alembic commands ###