# pylint: disable=E1101
# Standard Library
from unittest.mock import MagicMock

# First Party
from repository_scanner_backend.db import model
from repository_scanner_backend.db.model import DBrulePack
from repository_scanner_backend.resc_web_service.crud.rule import (
    get_all_rule_packs,
    get_newest_rule_pack,
    get_rule_packs_count,
    make_older_rule_packs_to_inactive
)

rule_packs = [
    ("0.0.1", "false", 1)
]


def test_get_newest_rule_pack():
    mock_conn = MagicMock()
    mock_conn.query.return_value.all.return_value = [
        DBrulePack("0.0.1", 1, False),
        DBrulePack("0.0.9", 1, False),
        DBrulePack("0.0.11", 1, False),
        DBrulePack("0.0.20", 1, True)
    ]
    newest_rule_pack = get_newest_rule_pack(mock_conn)
    assert newest_rule_pack.version == "0.0.20"


def test_get_rule_packs_count():
    mock_conn = MagicMock()
    mock_conn.query.return_value.scalar.return_value = 1
    _ = get_rule_packs_count(db_connection=mock_conn)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.scalar.assert_called_once()


def test_get_all_rule_packs():
    mock_conn = MagicMock()
    mock_conn.query.return_value.order_by.return_value.offset.return_value \
        .limit.return_value.all.return_value = rule_packs
    _ = get_all_rule_packs(db_connection=mock_conn, skip=0, limit=5)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.order_by.return_value. \
        offset.return_value.limit.return_value.all.assert_called_once()


def test_make_older_rule_packs_to_inactive():
    mock_conn = MagicMock()
    _ = make_older_rule_packs_to_inactive(latest_rule_pack_version="0.0.1", db_connection=mock_conn)
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    args = mock_conn.execute.call_args.args
    assert len(args) == 1
    assert args[0].is_update is True
    assert args[0].whereclause.left == model.rule_pack.DBrulePack.version
    assert args[0].whereclause.right.value == "0.0.1"
