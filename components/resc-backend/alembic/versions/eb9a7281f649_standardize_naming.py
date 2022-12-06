"""standardize naming

Revision ID: eb9a7281f649
Revises: f32ea53dce25
Create Date: 2022-10-27 16:04:14.494478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb9a7281f649'
down_revision = 'f32ea53dce25'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('repository_info', 'repository')
    op.rename_table('branch_info', 'branch')

    op.alter_column('branch', column_name='repository_info_id', new_column_name='repository_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)

    op.alter_column('finding', column_name='branch_info_id', new_column_name='branch_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)

    op.alter_column('scan', column_name='branch_info_id', new_column_name='branch_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)


def downgrade():
    op.rename_table('repository', 'repository_info')
    op.rename_table('branch', 'branch_info')

    op.alter_column('branch_info', column_name='repository_id', new_column_name='repository_info_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)

    op.alter_column('finding', column_name='branch_id', new_column_name='branch_info_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)

    op.alter_column('scan', column_name='branch_id', new_column_name='branch_info_id',
                    existing_type=sa.Integer(), type_=sa.Integer(),
                    existing_nullable=False, nullable=False)
