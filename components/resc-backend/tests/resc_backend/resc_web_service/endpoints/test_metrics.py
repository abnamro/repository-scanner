# Standard Library
import unittest
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import ANY, Mock, patch

# Third Party
import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# First Party
from resc_backend.constants import (
    CACHE_PREFIX,
    REDIS_CACHE_EXPIRE,
    RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME,
    RWS_ROUTE_AUDITED_COUNT_OVER_TIME,
    RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK,
    RWS_ROUTE_METRICS,
    RWS_ROUTE_PERSONAL_AUDITS,
    RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME,
    RWS_VERSION_PREFIX
)
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.cache_manager import CacheManager
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.endpoints.metrics import (
    convert_rows_to_finding_count_over_time,
    determine_audit_rank_current_week
)
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


@pytest.fixture(autouse=True)
def _init_cache() -> Generator[ANY, ANY, None]:
    FastAPICache.init(InMemoryBackend(),
                      prefix=CACHE_PREFIX,
                      expire=REDIS_CACHE_EXPIRE,
                      key_builder=CacheManager.request_key_builder,
                      enable=True)
    yield
    FastAPICache.reset()


class TestFindings(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

    @staticmethod
    def assert_cache(cached_response):
        assert FastAPICache.get_enable() is True
        assert FastAPICache.get_prefix() == CACHE_PREFIX
        assert FastAPICache.get_expire() == REDIS_CACHE_EXPIRE
        assert FastAPICache.get_key_builder() is not None
        assert FastAPICache.get_coder() is not None
        assert cached_response.headers.get("cache-control") is not None

    @patch("resc_backend.resc_web_service.crud.finding.get_finding_audit_status_count_over_time")
    def test_get_finding_audit_count_over_time(self, get_finding_audit_status_count_over_time):
        get_finding_audit_status_count_over_time.return_value = {}
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_AUDITED_COUNT_OVER_TIME}")

            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 13
            first_week = datetime.utcnow() - timedelta(weeks=0)
            nth_week = datetime.utcnow() - timedelta(weeks=len(data) - 1)
            assert data[len(data) - 1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                         f"W{first_week.isocalendar().week:02d}"
            assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_AUDITED_COUNT_OVER_TIME}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_finding_count_by_vcs_provider_over_time")
    def test_get_finding_total_count_over_time(self, get_finding_count_by_vcs_provider_over_time):
        get_finding_count_by_vcs_provider_over_time.return_value = {}
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK}")

            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 13
            first_week = datetime.utcnow() - timedelta(weeks=0)
            nth_week = datetime.utcnow() - timedelta(weeks=len(data) - 1)
            assert data[len(data) - 1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                         f"W{first_week.isocalendar().week:02d}"
            assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

            # Make the second request to retrieve response from cache
            cached_response = client.get(
                f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_un_triaged_finding_count_by_vcs_provider_over_time")
    def test_get_finding_un_triaged_count_over_time(self, get_un_triaged_finding_count_by_vcs_provider_over_time):
        get_un_triaged_finding_count_by_vcs_provider_over_time.return_value = {}
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME}")

            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 13
            first_week = datetime.utcnow() - timedelta(weeks=0)
            nth_week = datetime.utcnow() - timedelta(weeks=len(data) - 1)
            assert data[len(data) - 1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                         f"W{first_week.isocalendar().week:02d}"
            assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

            # Make the second request to retrieve response from cache
            cached_response = client.get(
                f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    def test_convert_rows_to_finding_count_over_time(self):
        first_week = datetime.utcnow() - timedelta(weeks=0)
        second_week = datetime.utcnow() - timedelta(weeks=1)
        third_week = datetime.utcnow() - timedelta(weeks=2)
        data1 = Mock(year=first_week.isocalendar().year, week=first_week.isocalendar().week,
                     provider_type=VCSProviders.AZURE_DEVOPS, finding_count=10)
        data2 = Mock(year=second_week.isocalendar().year, week=second_week.isocalendar().week,
                     provider_type=VCSProviders.AZURE_DEVOPS, finding_count=12)
        data3 = Mock(year=second_week.isocalendar().year, week=second_week.isocalendar().week,
                     provider_type=VCSProviders.BITBUCKET, finding_count=12)

        finding_counts = [data1, data2, data3]

        data = convert_rows_to_finding_count_over_time(finding_counts, weeks=3)
        assert len(data) == 3
        assert data[2].time_period == f"{first_week.isocalendar().year} W{first_week.isocalendar().week:02d}"
        assert data[2].vcs_provider_finding_count.AZURE_DEVOPS == getattr(data1, 'finding_count')
        assert data[2].total == getattr(data1, 'finding_count')
        assert data[1].time_period == f"{second_week.isocalendar().year} W{second_week.isocalendar().week:02d}"
        assert data[1].vcs_provider_finding_count.AZURE_DEVOPS == getattr(data2, 'finding_count')
        assert data[1].vcs_provider_finding_count.BITBUCKET == getattr(data3, 'finding_count')
        assert data[1].total == getattr(data2, 'finding_count') + getattr(data3, 'finding_count')
        assert data[0].time_period == f"{third_week.isocalendar().year} W{third_week.isocalendar().week:02d}"
        assert data[0].total == 0

    @patch("resc_backend.resc_web_service.crud.audit.get_audit_count_by_auditor_over_time")
    def test_get_audit_count_by_auditor_over_time(self, get_audit_count_by_auditor_over_time):
        get_audit_count_by_auditor_over_time.return_value = {}
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}"
                                  f"{RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME}")

            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 13
            first_week = datetime.utcnow() - timedelta(weeks=0)
            nth_week = datetime.utcnow() - timedelta(weeks=len(data) - 1)
            assert data[len(data) - 1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                         f"W{first_week.isocalendar().week:02d}"
            assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}"
                                         f"{RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.audit.get_audit_count_by_auditor_over_time")
    @patch("resc_backend.resc_web_service.crud.audit.get_personal_audit_count")
    def test_get_personal_audit_metrics(self, get_personal_audit_count, get_audit_count_by_auditor_over_time):
        get_personal_audit_count.return_value = 2
        get_audit_count_by_auditor_over_time.return_value = {}
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_PERSONAL_AUDITS}")

            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 7
            assert data["today"] == 2
            assert data["current_week"] == 2
            assert data["last_week"] == 2
            assert data["current_month"] == 2
            assert data["current_year"] == 2
            assert data["forever"] == 2
            assert data["rank_current_week"] == 0

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_PERSONAL_AUDITS}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.audit.get_audit_count_by_auditor_over_time")
    def test_determine_audit_rank_current_week(self, get_audit_count_by_auditor_over_time):
        get_audit_count_by_auditor_over_time.return_value = [Mock(auditor='Anonymous', audit_count=2),
                                                             Mock(auditor='Me', audit_count=4)]
        rank = determine_audit_rank_current_week(auditor='Anonymous', db_connection=None)
        assert rank == 2

    @patch("resc_backend.resc_web_service.crud.audit.get_audit_count_by_auditor_over_time")
    def test_determine_audit_rank_current_week_zero_audits(self, get_audit_count_by_auditor_over_time):
        get_audit_count_by_auditor_over_time.return_value = []
        rank = determine_audit_rank_current_week(auditor='Anonymous', db_connection=None)
        assert rank == 0
