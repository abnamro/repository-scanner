# Third Party
import pytest
from pydantic import ValidationError

# First Party
from vcs_scraper.constants import BITBUCKET
from vcs_scraper.model import VCSInstance


def test_vcs_instance_validation_wrong_provider_type():
    with pytest.raises(ValidationError):
        _ = VCSInstance(name="test_name3",
                        provider_type="NON_EXISTENT",
                        hostname="fake.node.com",
                        port=443,
                        scheme="https",
                        username="user",
                        password="password",
                        token="token",
                        exceptions=[],
                        scope=[])


def test_vcs_instance_validation_both_scope_and_exceptions():
    with pytest.raises(ValidationError):
        _ = VCSInstance(name="test_name3",
                        provider_type=BITBUCKET,
                        hostname="fake.node.com",
                        port=443,
                        scheme="https",
                        username="user",
                        password="password",
                        token="token",
                        exceptions=["project1"],
                        scope=["project2"])


def test_vcs_instance_validation_wrong_scheme():
    with pytest.raises(ValidationError):
        _ = VCSInstance(name="test_name3",
                        provider_type="NON_EXISTENT",
                        hostname="fake.node.com",
                        port=443,
                        scheme="ftp",
                        username="user",
                        password="password",
                        token="token",
                        exceptions=[],
                        scope=[])
