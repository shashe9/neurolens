"""neurolens_v2_migration

Revision ID: e2d5c17a515d
Revises: b6a8d6e90100
Create Date: 2026-06-13 23:12:43.673417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2d5c17a515d'
down_revision: Union[str, Sequence[str], None] = 'b6a8d6e90100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new tables
    op.create_table('domain_trend_snapshots',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('child_id', sa.Uuid(), nullable=False),
    sa.Column('domain_id', sa.Integer(), nullable=False),
    sa.Column('activity_count', sa.Integer(), nullable=False),
    sa.Column('variety_count', sa.Integer(), nullable=False),
    sa.Column('calculated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['child_id'], ['children.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['domain_id'], ['developmental_domains.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_domain_trend_snapshots_child_id'), 'domain_trend_snapshots', ['child_id'], unique=False)
    
    op.create_table('longitudinal_change_summaries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('child_id', sa.Uuid(), nullable=False),
    sa.Column('domain_id', sa.Integer(), nullable=False),
    sa.Column('summary_text', sa.Text(), nullable=False),
    sa.Column('detected_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['child_id'], ['children.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['domain_id'], ['developmental_domains.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_longitudinal_change_summaries_child_id'), 'longitudinal_change_summaries', ['child_id'], unique=False)
    
    op.create_table('recommendation_history',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('child_id', sa.Uuid(), nullable=False),
    sa.Column('recommendation_text', sa.Text(), nullable=False),
    sa.Column('domain_id', sa.Integer(), nullable=False),
    sa.Column('served_at', sa.DateTime(), nullable=False),
    sa.Column('interacted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['child_id'], ['children.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['domain_id'], ['developmental_domains.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_history_child_id'), 'recommendation_history', ['child_id'], unique=False)

    # Use batch_alter_table for SQLite compatibility when adding columns
    with op.batch_alter_table('children', schema=None) as batch_op:
        batch_op.add_column(sa.Column('initial_snapshot', sa.JSON(), nullable=True))

    with op.batch_alter_table('observations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('structured_body', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('structuring_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('embedding_vector', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('observations', schema=None) as batch_op:
        batch_op.drop_column('embedding_vector')
        batch_op.drop_column('structuring_status')
        batch_op.drop_column('structured_body')

    with op.batch_alter_table('children', schema=None) as batch_op:
        batch_op.drop_column('initial_snapshot')

    op.drop_index(op.f('ix_recommendation_history_child_id'), table_name='recommendation_history')
    op.drop_table('recommendation_history')
    op.drop_index(op.f('ix_longitudinal_change_summaries_child_id'), table_name='longitudinal_change_summaries')
    op.drop_table('longitudinal_change_summaries')
    op.drop_index(op.f('ix_domain_trend_snapshots_child_id'), table_name='domain_trend_snapshots')
    op.drop_table('domain_trend_snapshots')
    # ### end Alembic commands ###
