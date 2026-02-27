"""db_init

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-02-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'reports_daily_sales',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('total_orders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_paid_orders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_revenue_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cancelled_orders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_date'),
    )
    op.create_index(op.f('ix_reports_daily_sales_id'), 'reports_daily_sales', ['id'], unique=False)
    op.create_index(op.f('ix_reports_daily_sales_report_date'), 'reports_daily_sales', ['report_date'], unique=True)

    op.create_table(
        'order_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='PLN'),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id'),
    )
    op.create_index(op.f('ix_order_events_id'), 'order_events', ['id'], unique=False)
    op.create_index(op.f('ix_order_events_event_id'), 'order_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_order_events_event_type'), 'order_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_order_events_order_id'), 'order_events', ['order_id'], unique=False)

    op.create_table(
        'product_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('price_cents', sa.Integer(), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id'),
    )
    op.create_index(op.f('ix_product_events_id'), 'product_events', ['id'], unique=False)
    op.create_index(op.f('ix_product_events_event_id'), 'product_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_product_events_event_type'), 'product_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_product_events_product_id'), 'product_events', ['product_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_product_events_product_id'), table_name='product_events')
    op.drop_index(op.f('ix_product_events_event_type'), table_name='product_events')
    op.drop_index(op.f('ix_product_events_event_id'), table_name='product_events')
    op.drop_index(op.f('ix_product_events_id'), table_name='product_events')
    op.drop_table('product_events')

    op.drop_index(op.f('ix_order_events_order_id'), table_name='order_events')
    op.drop_index(op.f('ix_order_events_event_type'), table_name='order_events')
    op.drop_index(op.f('ix_order_events_event_id'), table_name='order_events')
    op.drop_index(op.f('ix_order_events_id'), table_name='order_events')
    op.drop_table('order_events')

    op.drop_index(op.f('ix_reports_daily_sales_report_date'), table_name='reports_daily_sales')
    op.drop_index(op.f('ix_reports_daily_sales_id'), table_name='reports_daily_sales')
    op.drop_table('reports_daily_sales')
