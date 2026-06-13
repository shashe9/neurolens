"""create suggestion feedback and validation study tables

Revision ID: b6a8d6e90100
Revises: f5a8a0c2b993
Create Date: 2026-06-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6a8d6e90100'
down_revision: Union[str, Sequence[str], None] = 'f5a8a0c2b993'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create suggestion_feedback table
    op.create_table(
        "suggestion_feedback",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=False),
        sa.Column("child_id", sa.UUID(), nullable=False),
        sa.Column("ai_suggestion_event_id", sa.UUID(), nullable=True),
        sa.Column("milestone_id", sa.UUID(), nullable=False),
        sa.Column("feedback_type", sa.String(length=50), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["parents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ai_suggestion_event_id"], ["ai_suggestion_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["milestone_id"], ["milestones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    
    # Create human_validation_sessions table
    op.create_table(
        "human_validation_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("participant_id", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("usability_score", sa.Integer(), nullable=False),
        sa.Column("trust_score", sa.Integer(), nullable=False),
        sa.Column("report_usefulness_score", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("human_validation_sessions")
    op.drop_table("suggestion_feedback")
