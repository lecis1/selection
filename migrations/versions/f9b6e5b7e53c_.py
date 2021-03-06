"""empty message

Revision ID: f9b6e5b7e53c
Revises: 61ad5db806c3
Create Date: 2020-12-15 11:02:04.367964

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f9b6e5b7e53c'
down_revision = '61ad5db806c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('records', 'select_number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('records', sa.Column('select_number', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
