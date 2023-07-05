"""remove branch

Revision ID: 44ac9602612b
Revises: 8dd0f349b5ad
Create Date: 2023-06-27 10:03:22.197295

"""
import logging
import sys

from alembic import op
import sqlalchemy as sa

from sqlalchemy.engine import Inspector

# revision identifiers, used by Alembic.
revision = '44ac9602612b'
down_revision = '8dd0f349b5ad'
branch_labels = None
depends_on = None

# Logger
logger = logging.getLogger()


def upgrade():
    inspector = Inspector.from_engine(op.get_bind())

    # add column repository_id to scan and finding
    op.add_column('finding', sa.Column('repository_id', sa.Integer(), nullable=True))
    op.add_column('scan', sa.Column('repository_id', sa.Integer(), nullable=True))
    # Fill it with corresponding contents
    op.execute("update finding "
               "set finding.repository_id = branch.repository_id "
               "from branch "
               "where branch.id = finding.branch_id")
    op.execute("update scan "
               "set scan.repository_id = branch.repository_id "
               "from branch "
               "where branch.id = scan.branch_id")
    # make repository_id not nullable
    op.alter_column('finding', 'repository_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('scan', 'repository_id', existing_type=sa.Integer(), nullable=False)
    # Add foreign key constraint from scan and finding to repository
    op.create_foreign_key('fk_finding_repository_id', 'finding', 'repository', ['repository_id'], ['id'])
    op.create_foreign_key('fk_scan_repository_id', 'scan', 'repository', ['repository_id'], ['id'])
    # Update unique constraint in finding with repository_id instead of branch_id
    op.drop_constraint('uc_finding_per_branch', 'finding', type_='unique')
    op.create_unique_constraint('uc_finding_per_repository', 'finding',
                                ['commit_id', 'repository_id', 'rule_name', 'file_path', 'line_number',
                                 'column_start', 'column_end'])
    # Drop column branch_id from finding and scan
    op.drop_constraint(get_foreign_key_name(inspector, 'finding', 'branch'), 'finding', type_='foreignkey')
    op.drop_column('finding', 'branch_id')
    op.drop_constraint(get_foreign_key_name(inspector, 'scan', 'branch'), 'scan', type_='foreignkey')
    op.drop_column('scan', 'branch_id')
    # Drop table branch
    op.drop_table('branch')


def downgrade():
    # Unable to make a reliable downgrade here as there would not be enough information in the database to restore the
    # branch table and re-link the finding and scan tables to it. Meaning that all findings would be invalidated
    pass


def get_foreign_key_name(inspector: Inspector, table_name: str, reference_table: str):
    foreign_keys = inspector.get_foreign_keys(table_name=table_name)
    for foreign_key in foreign_keys:
        if foreign_key["referred_table"] == reference_table:
            return foreign_key["name"]
    logger.error(f"Unable to find foreign key name for {table_name} referencing {reference_table}")
    sys.exit(-1)
