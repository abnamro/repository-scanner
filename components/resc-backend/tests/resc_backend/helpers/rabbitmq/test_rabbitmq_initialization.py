# Standard Library
import os
from unittest import mock
from unittest.mock import ANY, patch
from urllib import response

# Third Party
from requests import Session

# First Party
from resc_backend.constants import PROJECT_QUEUE, REPOSITORY_QUEUE

RESC_RABBITMQ_SERVICE_HOST = "fake-rabbitmq-host.com"
RESC_RABBITMQ_SERVICE_PORT_MGMT = "fake-rabbitmq-port"
RABBITMQ_DEFAULT_VHOST = "vhost"
RABBITMQ_DEFAULT_USER = "fake_rabbit_default_user"
RABBITMQ_DEFAULT_PASS = "fake_password"
RABBITMQ_USERNAME = "fake_rabbituser"
RABBITMQ_PASSWORD = "fake_password"

with mock.patch.dict(os.environ, {"RESC_RABBITMQ_SERVICE_HOST": RESC_RABBITMQ_SERVICE_HOST,
                                  "RESC_RABBITMQ_SERVICE_PORT_MGMT": RESC_RABBITMQ_SERVICE_PORT_MGMT,
                                  "RABBITMQ_DEFAULT_VHOST": RABBITMQ_DEFAULT_VHOST,
                                  "RABBITMQ_DEFAULT_USER": RABBITMQ_DEFAULT_USER,
                                  "RABBITMQ_DEFAULT_PASS": RABBITMQ_DEFAULT_PASS,
                                  "RABBITMQ_USERNAME": RABBITMQ_USERNAME,
                                  "RABBITMQ_PASSWORD": RABBITMQ_PASSWORD}):
    from resc_backend.helpers.rabbitmq import rabbitmq_initialization as rabbitmq_init  # noqa: E402  # isort:skip


@patch.object(Session, "get")
def test_wait_for_rabbitmq_server_to_up_is_successful(mock_get):
    response.status_code = 200
    mock_get.return_value = response
    result = rabbitmq_init.wait_for_rabbitmq_server_to_up(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url")
    assert result is True
    assert mock_get.call_count == 1


@patch.object(Session, "get")
def test_wait_for_rabbitmq_server_to_up_is_failed(mock_get):
    response.status_code = 500
    mock_get.return_value = response
    result = rabbitmq_init.wait_for_rabbitmq_server_to_up(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url")
    assert result is False
    assert mock_get.call_count == 1


@patch("requests.put")
def test_create_user_is_successful(mock_put):
    response.status_code = 201
    mock_put.return_value = response
    result = rabbitmq_init.create_user(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url", username="dummy_user",
                                       password="dummy_pwd", role="dummy_role")
    assert result is True
    assert mock_put.call_count == 1


@patch("requests.put")
def test_create_user_is_unsuccessful(mock_put):
    response.status_code = 500
    mock_put.return_value = response
    result = rabbitmq_init.create_user(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url", username="dummy_user",
                                       password="dummy_pwd", role="dummy_role")
    assert result is False
    assert mock_put.call_count == 1


@patch("requests.put")
def test_set_resource_permissions_is_successful(mock_put):
    response.status_code = 201
    mock_put.return_value = response
    result = rabbitmq_init.set_resource_permissions(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url",
                                                    v_host="dummy_v_host",
                                                    username="dummy_username", configure_resources_regex="dummy_regex",
                                                    read_resources_regex="dummy_regex",
                                                    write_resources_regex="dummy_regex")
    assert result is True
    assert mock_put.call_count == 1


@patch("requests.put")
def test_set_resource_permissions_is_unsuccessful(mock_put):
    response.status_code = 500
    mock_put.return_value = response
    result = rabbitmq_init.set_resource_permissions(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url",
                                                    v_host="dummy_v_host",
                                                    username="dummy_username", configure_resources_regex="dummy_regex",
                                                    read_resources_regex="dummy_regex",
                                                    write_resources_regex="dummy_regex")
    assert result is False
    assert mock_put.call_count == 1


@patch("requests.put")
def test_set_topic_permissions_is_successful(mock_put):
    response.status_code = 201
    mock_put.return_value = response
    result = rabbitmq_init.set_topic_permissions(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url",
                                                 v_host="dummy_v_host",
                                                 username="dummy_username", topic_name="dummy_topic_name",
                                                 allow_read=True, allow_write=True)
    assert result is True
    assert mock_put.call_count == 1


@patch("requests.put")
def test_set_topic_permissions_is_unsuccessful(mock_put):
    response.status_code = 500
    mock_put.return_value = response
    result = rabbitmq_init.set_topic_permissions(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url",
                                                 v_host="dummy_v_host",
                                                 username="dummy_username", topic_name="dummy_topic_name",
                                                 allow_read=True, allow_write=True)
    assert result is False
    assert mock_put.call_count == 1


@patch("resc_backend.helpers.rabbitmq.rabbitmq_initialization.set_topic_permissions")
@patch("resc_backend.helpers.rabbitmq.rabbitmq_initialization.set_resource_permissions")
@patch("resc_backend.helpers.rabbitmq.rabbitmq_initialization.create_user")
def test_create_queue_user_and_set_permission(mock_create_user, mock_set_resource_permissions,
                                              mock_set_topic_permissions):
    rabbitmq_init.create_queue_user_and_set_permission(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url")
    mock_create_user.assert_called_once_with(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url", username=ANY,
                                             password=ANY, role="monitoring")
    mock_set_resource_permissions.assert_called_once_with(rabbitmq_api_base_url="dummy-rabbitmq-api-base-url",
                                                          v_host="vhost", username="fake_rabbituser",
                                                          configure_resources_regex=f"^({PROJECT_QUEUE}"
                                                                                    f"|{REPOSITORY_QUEUE}"
                                                                                    f"|.*celery.*)$",
                                                          read_resources_regex=f"^{PROJECT_QUEUE}|{REPOSITORY_QUEUE}"
                                                                               f"|.*celery.*$",
                                                          write_resources_regex=f"^{PROJECT_QUEUE}|{REPOSITORY_QUEUE}"
                                                                                f"|amq.default|.*celery.*$")
    assert mock_set_topic_permissions.call_count == 2
