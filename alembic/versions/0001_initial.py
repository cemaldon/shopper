"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
    )

    op.create_table(
        'trips',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'trip_products',
        sa.Column('trip_id', sa.Integer(), sa.ForeignKey('trips.id'), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), primary_key=True),
    )


def downgrade():
    op.drop_table('trip_products')
    op.drop_table('trips')
    op.drop_table('products')
