"""empty message

Revision ID: 5876076a9c02
Revises: 7d30206ea574
Create Date: 2019-09-27 21:26:58.952115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5876076a9c02'
down_revision = '7d30206ea574'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('Venue_artist_id_fkey', 'Venue', type_='foreignkey')
    op.drop_column('Venue', 'artist_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Venue_artist_id_fkey', 'Venue', 'Artist', ['artist_id'], ['id'])
    op.drop_table('Show')
    # ### end Alembic commands ###
