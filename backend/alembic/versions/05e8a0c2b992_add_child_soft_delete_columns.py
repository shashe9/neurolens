"""add_child_soft_delete_columns

Revision ID: 05e8a0c2b992
Revises: 31e7376db48e
Create Date: 2026-06-12 00:15:21.689004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05e8a0c2b992'
down_revision: Union[str, Sequence[str], None] = '31e7376db48e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite requires batch operations to add columns with constraints or alter nullability
    with op.batch_alter_table("children") as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('deleted_by', sa.Uuid(), sa.ForeignKey('parents.id', name='fk_children_deleted_by_parents', ondelete='SET NULL'), nullable=True))
        batch_op.alter_column('gender', existing_type=sa.VARCHAR(length=50), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("children") as batch_op:
        batch_op.drop_column('deleted_by')
        batch_op.drop_column('deleted_at')
        batch_op.alter_column('gender', existing_type=sa.VARCHAR(length=50), nullable=False)
