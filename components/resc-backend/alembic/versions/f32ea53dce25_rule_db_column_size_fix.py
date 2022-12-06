"""Rule db column size fix

Revision ID: f32ea53dce25
Revises: e453b2238001
Create Date: 2022-10-19 14:13:17.452034

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f32ea53dce25'
down_revision = 'e453b2238001'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('rules', 'description',
                    existing_type=sa.String(length=400), type_=sa.String(length=2000),
                    existing_nullable=False, nullable=True)
    op.alter_column('rules', 'tags',
                    existing_type=sa.String(length=400), type_=sa.String(length=2000),
                    existing_nullable=True)
    op.alter_column('rules', 'regex',
                    existing_type=sa.String(length=1000), type_=sa.Text,
                    existing_nullable=True)
    op.alter_column('rules', 'path',
                    existing_type=sa.String(length=1000), type_=sa.Text,
                    existing_nullable=True)
    op.alter_column('rules', 'keywords',
                    existing_type=sa.String(length=400), type_=sa.Text,
                    existing_nullable=True)

    op.alter_column('rule_allow_list', 'description',
                    existing_type=sa.String(length=400), type_=sa.String(length=2000),
                    existing_nullable=False, nullable=True)
    op.alter_column('rule_allow_list', 'regexes',
                    existing_type=sa.String(length=400), type_=sa.Text,
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'paths',
                    existing_type=sa.String(length=400), type_=sa.Text,
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'commits',
                    existing_type=sa.String(length=400), type_=sa.Text,
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'stop_words',
                    existing_type=sa.String(length=400), type_=sa.Text,
                    existing_nullable=True)


def downgrade():
    op.alter_column('rules', 'description',
                    existing_type=sa.String(length=2000), type_=sa.String(length=400),
                    existing_nullable=True, nullable=False)
    op.alter_column('rules', 'tags',
                    existing_type=sa.String(length=2000), type_=sa.String(length=400),
                    existing_nullable=True)
    op.alter_column('rules', 'regex',
                    existing_type=sa.Text, type_=sa.String(length=1000),
                    existing_nullable=True)
    op.alter_column('rules', 'path',
                    existing_type=sa.Text, type_=sa.String(length=1000),
                    existing_nullable=True)
    op.alter_column('rules', 'keywords',
                    existing_type=sa.Text, type_=sa.String(length=400),
                    existing_nullable=True)

    op.alter_column('rule_allow_list', 'description',
                    existing_type=sa.String(length=2000), type_=sa.String(length=400),
                    existing_nullable=True, nullable=False)
    op.alter_column('rule_allow_list', 'regexes',
                    existing_type=sa.Text, type_=sa.String(length=400),
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'paths',
                    existing_type=sa.Text, type_=sa.String(length=400),
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'commits',
                    existing_type=sa.Text, type_=sa.String(length=400),
                    existing_nullable=True)
    op.alter_column('rule_allow_list', 'stop_words',
                    existing_type=sa.Text, type_=sa.String(length=400),
                    existing_nullable=True)
