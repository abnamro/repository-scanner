"""empty message

Revision ID: 9c5fa6db20f1
Revises: ar399258p714
Create Date: 2023-03-06 13:56:47.958406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c5fa6db20f1'
down_revision = 'ar399258p714'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('finding', sa.Column('column_start', sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column('finding', sa.Column('column_end', sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.drop_constraint('uc_finding_per_branch', 'finding', type_='unique')
    op.create_unique_constraint('uc_finding_per_branch', 'finding',
                                ['commit_id', 'branch_id', 'rule_name', 'file_path', 'line_number',
                                 'column_start', 'column_end'])


def downgrade():
    op.drop_constraint('uc_finding_per_branch', 'finding', type_='unique')
    op.create_unique_constraint('uc_finding_per_branch', 'finding',
                                ['commit_id', 'branch_id', 'rule_name', 'file_path', 'line_number'])
    op.drop_column('finding', 'column_start')
    op.drop_column('finding', 'column_end')
