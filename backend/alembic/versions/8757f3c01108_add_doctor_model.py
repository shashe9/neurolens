"""add_doctor_model

Revision ID: 8757f3c01108
Revises: 5baf0e3ffbe1
Create Date: 2026-06-15 17:16:01.665491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8757f3c01108'
down_revision: Union[str, Sequence[str], None] = '5baf0e3ffbe1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('doctors',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('specialization', sa.String(length=255), nullable=True),
    sa.Column('clinic_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doctors_email'), 'doctors', ['email'], unique=True)

    with op.batch_alter_table('clinical_visits', schema=None) as batch_op:
        batch_op.add_column(sa.Column('doctor_id', sa.Uuid(), nullable=True))
        batch_op.create_foreign_key('fk_clinical_visits_doctor_id_doctors', 'doctors', ['doctor_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('clinical_visits', schema=None) as batch_op:
        batch_op.drop_constraint('fk_clinical_visits_doctor_id_doctors', type_='foreignkey')
        batch_op.drop_column('doctor_id')
    op.drop_index(op.f('ix_doctors_email'), table_name='doctors')
    op.drop_table('doctors')

