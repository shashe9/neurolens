"""add_recommendation_feedback_and_activity_outcomes

Revision ID: 5baf0e3ffbe1
Revises: cd8371253e10
Create Date: 2026-06-14 19:21:13.638971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5baf0e3ffbe1'
down_revision: Union[str, Sequence[str], None] = 'cd8371253e10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'activity_outcomes' not in tables:
        op.create_table('activity_outcomes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('child_id', sa.Uuid(), nullable=False),
        sa.Column('activity_id', sa.String(length=100), nullable=False),
        sa.Column('attempted', sa.Boolean(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('parent_notes', sa.Text(), nullable=True),
        sa.Column('observed_change', sa.Text(), nullable=True),
        sa.Column('logged_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['child_id'], ['children.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_activity_outcomes_child_id'), 'activity_outcomes', ['child_id'], unique=False)

    if 'recommendation_feedback' not in tables:
        op.create_table('recommendation_feedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('child_id', sa.Uuid(), nullable=False),
        sa.Column('recommendation_id', sa.String(length=100), nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),
        sa.Column('shown_at', sa.DateTime(), nullable=False),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('helpful', sa.Boolean(), nullable=True),
        sa.Column('dismissed', sa.Boolean(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['child_id'], ['children.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_recommendation_feedback_child_id'), 'recommendation_feedback', ['child_id'], unique=False)

    columns = [c['name'] for c in inspector.get_columns('observations')]
    if 'quality_score' not in columns:
        op.add_column('observations', sa.Column('quality_score', sa.Float(), server_default='1.0', nullable=False))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('observations', 'quality_score')
    op.drop_index(op.f('ix_recommendation_feedback_child_id'), table_name='recommendation_feedback')
    op.drop_table('recommendation_feedback')
    op.drop_index(op.f('ix_activity_outcomes_child_id'), table_name='activity_outcomes')
    op.drop_table('activity_outcomes')

