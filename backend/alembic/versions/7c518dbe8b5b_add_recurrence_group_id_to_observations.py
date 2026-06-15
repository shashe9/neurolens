"""add_recurrence_group_id_to_observations

Revision ID: 7c518dbe8b5b
Revises: e2d5c17a515d
Create Date: 2026-06-14 00:13:44.991073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c518dbe8b5b'
down_revision: Union[str, Sequence[str], None] = 'e2d5c17a515d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('observations', sa.Column('recurrence_group_id', sa.Uuid(), nullable=True))
    op.create_index('idx_obs_recurrence_group', 'observations', ['recurrence_group_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_obs_recurrence_group', table_name='observations')
    op.drop_column('observations', 'recurrence_group_id')
