"""empty message

Revision ID: 2046b8c25f68
Revises: fa84e1cbdfe9
Create Date: 2018-10-24 23:09:42.332185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2046b8c25f68'
down_revision = 'fa84e1cbdfe9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserData',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_id', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id', 'line_id')
    )
    op.drop_table('PictureDate')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('PictureDate',
    sa.Column('Id', sa.INTEGER(), nullable=False),
    sa.Column('Uuid', sa.VARCHAR(length=64), nullable=True),
    sa.Column('Title', sa.VARCHAR(length=64), nullable=True),
    sa.Column('Description', sa.VARCHAR(length=128), nullable=True),
    sa.PrimaryKeyConstraint('Id'),
    sa.UniqueConstraint('Uuid')
    )
    op.drop_table('UserData')
    # ### end Alembic commands ###
