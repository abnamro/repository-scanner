"""rule tags

Revision ID: 8dd0f349b5ad
Revises: ar7fh3ac2071
Create Date: 2023-05-02 10:10:20.423021

"""
import logging

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy.engine import Inspector

revision = '8dd0f349b5ad'
down_revision = 'ar7fh3ac2071'
branch_labels = None
depends_on = None

# Logger
logger = logging.getLogger()


def upgrade():
    inspector = Inspector.from_engine(op.get_bind())

    drop_if_exist(inspector, "tag")
    if not inspector.has_table("tag"):
        logger.info("Creating table tag")
        op.create_table("tag",
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('name', sa.String(length=200), nullable=False),
                        sa.PrimaryKeyConstraint('id')
                        )

    drop_if_exist(inspector, "rule_tag")
    if not inspector.has_table("rule_tag"):
        logger.info("Creating table rule_tag")
        op.create_table('rule_tag',
                        sa.Column('rule_id', sa.Integer(), nullable=False),
                        sa.Column('tag_id', sa.Integer(), nullable=False),
                        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ),
                        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
                        sa.PrimaryKeyConstraint('rule_id', 'tag_id'),
                        )
    # insert data in to tag table
    logger.info("Inserting data in to tag table")
    op.execute("INSERT INTO tag (name) "
               "select distinct cs.Value as name from rules "
               "cross apply STRING_SPLIT(tags, ',') cs")

    # insert data in to rule_tag table
    logger.info("Inserting data in to rule_tag table")
    op.execute("INSERT INTO rule_tag (rule_id, tag_id) "
               "select rules.id, tag.id from rules "
               "cross apply STRING_SPLIT(tags, ',') cs join tag on tag.name = cs.Value")

    # Drop tags column from rules table
    logger.info("Drop tags column from rules table")
    op.drop_column('rules', 'tags')


def downgrade():
    # add tags column to rules
    op.add_column('rules', sa.Column('tags', sa.String(length=2000), nullable=True))

    # insert data in to rules table
    logger.info("Update tags in rules table")
    op.execute("update rules set tags = ("
               "SELECT STRING_AGG(tag.name, ',') as tags "
               "FROM rule_tag "
               "JOIN tag ON tag.id = rule_tag.tag_id "
               "where rule_id = rules.id "
               "GROUP BY rule_id)")

    # drop rule_tag and tag tables
    op.drop_table('tag')
    op.drop_table('rule_tag')


def drop_if_exist(inspector: Inspector, table_name: str):
    if inspector.has_table(table_name):
        logger.info(f"Dropping table {table_name}")
        op.drop_table(table_name)
