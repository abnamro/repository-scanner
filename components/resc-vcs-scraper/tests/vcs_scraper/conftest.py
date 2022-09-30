# Third Party
import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('RESC_RABBITMQ_SERVICE_HOST', 'fake-rabbitmq-host.com')
    monkeypatch.setenv('RABBITMQ_DEFAULT_VHOST', 'vhost')
    monkeypatch.setenv('RABBITMQ_QUEUES_USERNAME', 'fake_rabbituser')
    monkeypatch.setenv('RABBITMQ_QUEUES_PASSWORD', 'fake_password')
    monkeypatch.setenv('VCS_INSTANCES_FILE_PATH', 'fake_path.json')
