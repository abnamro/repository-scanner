# pylint: disable=E1101
# Standard Library
import operator

# Third Party
from mock.mock import MagicMock

# First Party
from resc_backend.constants import BITBUCKET
from resc_backend.db import model
from resc_backend.resc_web_service.crud.vcs_instance import (
    create_vcs_instance,
    create_vcs_instance_if_not_exists,
    delete_vcs_instance,
    get_vcs_instance,
    get_vcs_instances,
    get_vcs_instances_count,
    update_vcs_instance
)
from resc_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate

vcs_instances = [
    (1, "vcs server 1", BITBUCKET, "https", "host1.com", 443, None, [], [])
]


def test_get_vcs_instance():
    mock_conn = MagicMock()
    mock_conn.query.return_value.filter.return_value.first.return_value = vcs_instances[0]
    _ = get_vcs_instance(mock_conn, 1)

    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.id_
    assert args[0].right.value == 1
    assert args[0].operator == operator.eq


def test_get_vcs_instances():
    mock_conn = MagicMock()
    mock_conn.query.return_value.order_by.return_value.offset.return_value\
        .limit.return_value.all.return_value = vcs_instances
    _ = get_vcs_instances(mock_conn)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_not_called()


def test_get_vcs_instances_filter_by_vcs_provider_type():
    mock_conn = MagicMock()
    mock_conn.query.return_value.order_by.return_value.offset.return_value\
        .limit.return_value.all_return_value = vcs_instances
    _ = get_vcs_instances(mock_conn, vcs_provider_type=BITBUCKET)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    mock_conn.query.return_value.filter.return_value.filter.assert_not_called()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.provider_type
    assert args[0].right.value == BITBUCKET
    assert args[0].operator == operator.eq


def test_get_vcs_instances_filter_by_vcs_instance_name():
    mock_conn = MagicMock()
    mock_conn.query.return_value.order_by.return_value.offset.return_value\
        .limit.return_value.all_return_value = vcs_instances
    _ = get_vcs_instances(mock_conn, vcs_instance_name="server 1")
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    mock_conn.query.return_value.filter.return_value.filter.assert_not_called()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.name
    assert args[0].right.value == "server 1"
    assert args[0].operator == operator.eq


def test_get_vcs_instances_filter_by_vcs_instance_name_and_vcs_provider_type():
    mock_conn = MagicMock()
    mock_conn.query.return_value.order_by.return_value.offset.return_value\
        .limit.return_value.all_return_value = vcs_instances
    _ = get_vcs_instances(mock_conn, vcs_instance_name="server 1", vcs_provider_type=BITBUCKET)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.provider_type
    assert args[0].right.value == BITBUCKET
    assert args[0].operator == operator.eq

    mock_conn.query.return_value.filter.return_value.filter.assert_called_once()
    args = mock_conn.query.return_value.filter.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.name
    assert args[0].right.value == "server 1"
    assert args[0].operator == operator.eq

    mock_conn.query.return_value.filter.return_value.filter.return_value.order_by.return_value.\
        offset.return_value.limit.return_value.all.assert_called_once()


def test_get_vcs_instances_count():
    mock_conn = MagicMock()
    mock_conn.query.return_value.scalar.return_value = 1
    _ = get_vcs_instances_count(mock_conn)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.scalar.assert_called_once()


def test_get_vcs_instances_count_filter_by_vcs_provider_type():
    mock_conn = MagicMock()
    mock_conn.query.return_value.filter.return_value.scalar.return_value = 2
    _ = get_vcs_instances_count(mock_conn, vcs_provider_type=BITBUCKET)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.provider_type
    assert args[0].right.value == BITBUCKET
    assert args[0].operator == operator.eq


def test_get_vcs_instances_count_filter_by_vcs_instance_name():
    mock_conn = MagicMock()
    mock_conn.query.return_value.filter.return_value.scalar.return_value = 2
    _ = get_vcs_instances_count(mock_conn, vcs_instance_name=BITBUCKET)
    mock_conn.query.assert_called_once()
    mock_conn.query.return_value.filter.assert_called_once()
    args = mock_conn.query.return_value.filter.call_args.args

    assert len(args) == 1
    assert args[0].left == model.DBVcsInstance.name
    assert args[0].right.value == BITBUCKET
    assert args[0].operator == operator.eq


def test_update_vcs_instance():
    mock_conn = MagicMock()
    before_update_db_vcs_instance = model.DBVcsInstance(name="test_name1",
                                                        provider_type=BITBUCKET,
                                                        hostname="fake.host.com",
                                                        port=443,
                                                        scheme="https",
                                                        exceptions="",
                                                        scope="",
                                                        organization="")
    after_update_vcs_instance = VCSInstanceCreate(name="test_name2",
                                                  provider_type=BITBUCKET,
                                                  hostname="fake.host2.com",
                                                  port=444,
                                                  scheme="http",
                                                  exceptions=["test"],
                                                  scope=[],
                                                  organization="")

    after_update_db_vcs_instance = model.DBVcsInstance(name="test_name2",
                                                       provider_type=BITBUCKET,
                                                       hostname="fake.host2.com",
                                                       port=444,
                                                       scheme="http",
                                                       exceptions="test",
                                                       scope="",
                                                       organization="")

    mock_conn.query.return_value.filter_by.return_value.first.return_value = before_update_db_vcs_instance
    update_vcs_instance(mock_conn, 1, after_update_vcs_instance)
    mock_conn.refresh.assert_called_once()
    result = mock_conn.refresh.call_args.args[0]

    assert result.name == after_update_db_vcs_instance.name
    assert result.hostname == after_update_db_vcs_instance.hostname
    assert result.port == after_update_db_vcs_instance.port
    assert result.provider_type == after_update_db_vcs_instance.provider_type
    assert result.exceptions == after_update_db_vcs_instance.exceptions
    assert result.scope == after_update_db_vcs_instance.scope
    assert result.scheme == after_update_db_vcs_instance.scheme
    assert result.organization == after_update_db_vcs_instance.organization
    assert result.id_ == after_update_db_vcs_instance.id_


def test_create_vcs_instance():
    mock_conn = MagicMock()
    vcs_instance = VCSInstanceCreate(name="test_name2",
                                     provider_type=BITBUCKET,
                                     hostname="fake.host2.com",
                                     port=444,
                                     scheme="http",
                                     exceptions=["test"],
                                     scope=[],
                                     organization="")
    create_vcs_instance(mock_conn, vcs_instance)
    mock_conn.add.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.refresh.assert_called_once()

    result = mock_conn.add.call_args.args[0]

    assert result.name == vcs_instance.name
    assert result.hostname == vcs_instance.hostname
    assert result.port == vcs_instance.port
    assert result.provider_type == vcs_instance.provider_type
    assert result.exceptions == ",".join(vcs_instance.exceptions)
    assert result.scope == ",".join(vcs_instance.scope)
    assert result.scheme == vcs_instance.scheme
    assert result.organization == vcs_instance.organization


def test_create_vcs_instance_if_not_exists():
    mock_conn = MagicMock()
    mock_conn.query.return_value.filter.return_value.first.return_value = None

    vcs_instance = VCSInstanceCreate(name="test_name2",
                                     provider_type=BITBUCKET,
                                     hostname="fake.host2.com",
                                     port=444,
                                     scheme="http",
                                     exceptions=["test"],
                                     scope=[],
                                     organization="")
    create_vcs_instance_if_not_exists(mock_conn, vcs_instance)
    mock_conn.query.return_value.filter.return_value.first.assert_called_once()
    mock_conn.add.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.refresh.assert_called_once()

    result = mock_conn.add.call_args.args[0]

    assert result.name == vcs_instance.name
    assert result.hostname == vcs_instance.hostname
    assert result.port == vcs_instance.port
    assert result.provider_type == vcs_instance.provider_type
    assert result.exceptions == ",".join(vcs_instance.exceptions)
    assert result.scope == ",".join(vcs_instance.scope)
    assert result.scheme == vcs_instance.scheme
    assert result.organization == vcs_instance.organization


def test_create_vcs_instance_if_not_exists_when_vcs_instance_exists():
    mock_conn = MagicMock()
    vcs_instance = VCSInstanceCreate(name="test_name2",
                                     provider_type=BITBUCKET,
                                     hostname="fake.host2.com",
                                     port=444,
                                     scheme="http",
                                     exceptions=["test"],
                                     scope=[],
                                     organization="")

    mock_conn.query.return_value.filter.return_value.first.return_value = (vcs_instance,)
    create_vcs_instance_if_not_exists(mock_conn, vcs_instance)
    mock_conn.query.return_value.filter.return_value.first.assert_called_once()
    mock_conn.add.assert_not_called()


def test_delete_vcs_instance():
    mock_conn = MagicMock()
    vcs_instance = VCSInstanceCreate(name="test_name2",
                                     provider_type=BITBUCKET,
                                     hostname="fake.host2.com",
                                     port=444,
                                     scheme="http",
                                     exceptions=["test"],
                                     scope=[],
                                     organization="")
    mock_conn.query.return_value.filter_by.return_value.first.return_value = vcs_instance
    delete_vcs_instance(mock_conn, 1)
    mock_conn.delete.assert_called_once()
    mock_conn.commit.assert_called_once()

    result = mock_conn.delete.call_args.args[0]

    assert result.name == vcs_instance.name
    assert result.hostname == vcs_instance.hostname
    assert result.port == vcs_instance.port
    assert result.provider_type == vcs_instance.provider_type
    assert result.exceptions == vcs_instance.exceptions
    assert result.scope == vcs_instance.scope
    assert result.scheme == vcs_instance.scheme
    assert result.organization == vcs_instance.organization
