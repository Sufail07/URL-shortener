"""create urls table

Revision ID: bd4835b3c508
Revises: 
Create Date: 2026-08-19 19:13:01.523782
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bd4835b3c508'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_url', sa.String(), nullable=False),
        sa.Column('short_code', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('short_code'),
    )


def downgrade() -> None:
    op.drop_table('urls')
