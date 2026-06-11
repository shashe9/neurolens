"""create_observation_milestone_evidence_table

Revision ID: a3e74fd30f8a
Revises: 05e8a0c2b992
Create Date: 2026-06-12 00:25:00.413265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3e74fd30f8a'
down_revision: Union[str, Sequence[str], None] = '05e8a0c2b992'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the new junction table
    op.create_table('observation_milestone_evidence',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('observation_id', sa.Uuid(), nullable=False),
    sa.Column('milestone_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['observation_id'], ['observations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # 2. Data Migration: Copy old observations.milestone_id into new table
    connection = op.get_bind()
    import uuid
    from datetime import datetime
    
    obs_table = sa.table(
        'observations',
        sa.column('id', sa.Uuid),
        sa.column('milestone_id', sa.Uuid)
    )
    evidence_table = sa.table(
        'observation_milestone_evidence',
        sa.column('id', sa.Uuid),
        sa.column('observation_id', sa.Uuid),
        sa.column('milestone_id', sa.Uuid),
        sa.column('created_at', sa.DateTime)
    )
    
    # Select rows with non-null milestone_id
    results = connection.execute(sa.select(obs_table.c.id, obs_table.c.milestone_id).where(obs_table.c.milestone_id.isnot(None))).fetchall()
    for row in results:
        connection.execute(evidence_table.insert().values(
            id=uuid.uuid4(),
            observation_id=row[0],
            milestone_id=row[1],
            created_at=datetime.utcnow()
        ))

    # 3. Migrate milestone statuses to new terms
    statuses_table = sa.table(
        'milestone_statuses',
        sa.column('id', sa.Uuid),
        sa.column('status', sa.String)
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'not_started')
        .values(status='not_observed')
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'in_progress')
        .values(status='emerging')
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'achieved')
        .values(status='observed')
    )

    # 4. Remove direct column from observations using batch mode for SQLite
    with op.batch_alter_table("observations") as batch_op:
        batch_op.drop_column('milestone_id')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Add direct column back to observations using batch mode
    with op.batch_alter_table("observations") as batch_op:
        batch_op.add_column(sa.Column('milestone_id', sa.Uuid(), sa.ForeignKey('milestones.id', name='fk_observations_milestone_id', ondelete='SET NULL'), nullable=True))

    # 2. Migrate data back (first supporting milestone mapping only)
    connection = op.get_bind()
    evidence_table = sa.table(
        'observation_milestone_evidence',
        sa.column('observation_id', sa.Uuid),
        sa.column('milestone_id', sa.Uuid)
    )
    obs_table = sa.table(
        'observations',
        sa.column('id', sa.Uuid),
        sa.column('milestone_id', sa.Uuid)
    )
    
    results = connection.execute(sa.select(evidence_table.c.observation_id, evidence_table.c.milestone_id)).fetchall()
    updated_obs = set()
    for row in results:
        obs_id = row[0]
        milestone_id = row[1]
        if obs_id not in updated_obs:
            connection.execute(
                obs_table.update()
                .where(obs_table.c.id == obs_id)
                .values(milestone_id=milestone_id)
            )
            updated_obs.add(obs_id)

    # 3. Migrate milestone statuses back
    statuses_table = sa.table(
        'milestone_statuses',
        sa.column('id', sa.Uuid),
        sa.column('status', sa.String)
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'not_observed')
        .values(status='not_started')
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'emerging')
        .values(status='in_progress')
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'observed')
        .values(status='achieved')
    )
    connection.execute(
        statuses_table.update()
        .where(statuses_table.c.status == 'consistently_demonstrated')
        .values(status='achieved')
    )

    # 4. Drop the junction table
    op.drop_table('observation_milestone_evidence')
