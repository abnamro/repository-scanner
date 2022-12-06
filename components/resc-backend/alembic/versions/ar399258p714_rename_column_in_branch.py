"""Renaming last_scanned_commit column to latest_commit in branch table

Revision ID: ar399258p714
Revises: eb9a7281f649
Create Date: 2022-12-06 16:04:14.494478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ar399258p714'
down_revision = 'eb9a7281f649'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('branch', column_name='last_scanned_commit', new_column_name='latest_commit',
                    existing_type=sa.String(length=100), type_=sa.String(length=100),
                    existing_nullable=False, nullable=False)


def downgrade():
    op.alter_column('branch', column_name='latest_commit', new_column_name='last_scanned_commit',
                    existing_type=sa.String(length=100), type_=sa.String(length=100),
                    existing_nullable=False, nullable=False)
