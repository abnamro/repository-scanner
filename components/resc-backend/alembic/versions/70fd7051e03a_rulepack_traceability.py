"""rulepack traceability

Revision ID: 70fd7051e03a
Revises: 44ac9602612b
Create Date: 2023-08-15 10:44:17.483160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70fd7051e03a'
down_revision = '44ac9602612b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('rule_pack', sa.Column('created', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade():
    op.drop_column('rule_pack', 'created')
