"""Testing Alembic to see what whistles it blows

Revision ID: 8fe7674e9310
Revises: 
Create Date: 2023-11-16 12:08:58.282648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fe7674e9310'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('agencies', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('calendar', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('geoshapes', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('routes', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('stop_times', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('stops', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    op.alter_column('trips', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trips', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('stops', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('stop_times', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('routes', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('geoshapes', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('calendar', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.alter_column('agencies', 'feed_id',
               existing_type=sa.VARCHAR(length=63),
               nullable=True)
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    # ### end Alembic commands ###
