"""audit_history

Revision ID: ar7fh3ac2071
Revises: 9c5fa6db20f1
Create Date: 2023-04-03 16:21:59.958406

"""
import logging

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'ar7fh3ac2071'
down_revision = '9c5fa6db20f1'
branch_labels = None
depends_on = None

# Logger
logger = logging.getLogger()

# Table names
FINDING = 'finding'
AUDIT = 'audit'


def upgrade():
    inspector = Inspector.from_engine(op.get_bind())

    # create audit table with temporary finding_id column
    drop_if_exist(inspector, AUDIT)
    if not inspector.has_table(AUDIT):
        logger.info(f"Creating table {AUDIT}")
        op.create_table(AUDIT,
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('finding_id', sa.Integer(), nullable=False),
                        sa.Column('status',
                                  sa.Enum('NOT_ANALYZED', 'UNDER_REVIEW', 'CLARIFICATION_REQUIRED', 'FALSE_POSITIVE',
                                          'TRUE_POSITIVE', name='findingstatus'), server_default='NOT_ANALYZED',
                                  nullable=False),
                        sa.Column('auditor', sa.String(length=200), nullable=True),
                        sa.Column('comment', sa.String(length=255), nullable=True),
                        sa.Column('timestamp', sa.DateTime(), nullable=False),
                        sa.PrimaryKeyConstraint('id')
                        )

    # insert data in to audit table
    logger.info(f"Inserting data in to {AUDIT} table")
    op.execute(f"INSERT INTO {AUDIT} (status, comment, auditor, timestamp, finding_id) "
               f"SELECT status, comment,'Anonymous' as auditor, CURRENT_TIMESTAMP as timestamp, id FROM {FINDING}")

    # Remove the default value constraint for status column
    logger.info(f"Remove default value constraint for status column from {FINDING} table")
    op.alter_column(FINDING, 'status',
                    existing_type=sa.Enum('NOT_ANALYZED', 'UNDER_REVIEW', 'CLARIFICATION_REQUIRED', 'FALSE_POSITIVE',
                                          'TRUE_POSITIVE', name='findingstatus'), server_default=None, nullable=True)
    # Drop status column from finding table
    logger.info(f"Drop status column from {FINDING} table")
    op.drop_column(FINDING, 'status')

    # Drop comment column from finding table
    logger.info(f"Drop comment column from {FINDING} table")
    op.drop_column(FINDING, 'comment')


def downgrade():
    logger.info(f"Downgrading from revision {revision} to {down_revision}")
    inspector = Inspector.from_engine(op.get_bind())

    op.add_column(FINDING, sa.Column('status',
                                     sa.Enum('NOT_ANALYZED', 'UNDER_REVIEW', 'CLARIFICATION_REQUIRED', 'FALSE_POSITIVE',
                                             'TRUE_POSITIVE',
                                             name='findingstatus'), server_default='NOT_ANALYZED', nullable=False))

    op.add_column(FINDING, sa.Column('comment', sa.String(length=255), nullable=True))

    # Populate the status and comment from audit table to finding table
    op.execute(f"UPDATE {FINDING} "
               "SET status = status_comments.status, comment = status_comments.comment "
               f"FROM (select a.id, a.status, a.comment, a.finding_id from audit1 a ) "
               f"as status_comments WHERE finding.id = status_comments.finding_id")

    drop_if_exist(inspector, AUDIT)


def drop_if_exist(inspector: Inspector, table_name: str):
    if inspector.has_table(table_name):
        logger.info(f"Dropping table {table_name}")
        op.drop_table(table_name)
