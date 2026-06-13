"""add_parent_hashed_password

Revision ID: f5a8a0c2b993
Revises: 05e8a0c2b992
Create Date: 2026-06-13 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a8a0c2b993'
down_revision: Union[str, Sequence[str], None] = '2d4906a1b5bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite requires batch operations to safely alter table schemas
    with op.batch_alter_table("parents") as batch_op:
        batch_op.add_column(sa.Column('hashed_password', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("parents") as batch_op:
        batch_op.drop_column('hashed_password')
