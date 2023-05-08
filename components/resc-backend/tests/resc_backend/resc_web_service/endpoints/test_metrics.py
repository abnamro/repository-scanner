# Standard Library
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import (
    RWS_ROUTE_AUDITED_COUNT_OVER_TIME,
    RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK,
    RWS_ROUTE_METRICS,
    RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME,
    RWS_VERSION_PREFIX
)
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.endpoints.metrics import convert_rows_to_finding_count_over_time
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


class TestFindings(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

    @patch("resc_backend.resc_web_service.crud.finding.get_finding_audit_status_count_over_time")
    def test_get_finding_audit_count_over_time(self, get_finding_audit_status_count_over_time):
        get_finding_audit_status_count_over_time.return_value = {}
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_AUDITED_COUNT_OVER_TIME}")

        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 13
        first_week = datetime.utcnow() - timedelta(weeks=0)
        nth_week = datetime.utcnow() - timedelta(weeks=len(data)-1)
        assert data[len(data)-1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                   f"W{first_week.isocalendar().week:02d}"
        assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

    @patch("resc_backend.resc_web_service.crud.finding.get_finding_count_by_vcs_provider_over_time")
    def test_get_finding_total_count_over_time(self, get_finding_count_by_vcs_provider_over_time):
        get_finding_count_by_vcs_provider_over_time.return_value = {}
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK}")

        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 13
        first_week = datetime.utcnow() - timedelta(weeks=0)
        nth_week = datetime.utcnow() - timedelta(weeks=len(data)-1)
        assert data[len(data)-1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                   f"W{first_week.isocalendar().week:02d}"
        assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

    @patch("resc_backend.resc_web_service.crud.finding.get_un_triaged_finding_count_by_vcs_provider_over_time")
    def test_get_finding_un_triaged_count_over_time(self, get_un_triaged_finding_count_by_vcs_provider_over_time):
        get_un_triaged_finding_count_by_vcs_provider_over_time.return_value = {}
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_METRICS}{RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME}")

        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 13
        first_week = datetime.utcnow() - timedelta(weeks=0)
        nth_week = datetime.utcnow() - timedelta(weeks=len(data)-1)
        assert data[len(data)-1]["time_period"] == f"{first_week.isocalendar().year} " \
                                                   f"W{first_week.isocalendar().week:02d}"
        assert data[0]["time_period"] == f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"

    def test_convert_rows_to_finding_count_over_time(self):
        first_week = datetime.utcnow() - timedelta(weeks=0)
        second_week = datetime.utcnow() - timedelta(weeks=1)
        third_week = datetime.utcnow() - timedelta(weeks=2)
        data1 = {"year": first_week.isocalendar().year, "week": first_week.isocalendar().week,
                 "provider_type": VCSProviders.AZURE_DEVOPS, "finding_count": 10}
        data2 = {"year": second_week.isocalendar().year, "week": second_week.isocalendar().week,
                 "provider_type": VCSProviders.AZURE_DEVOPS, "finding_count": 12}
        data3 = {"year": second_week.isocalendar().year, "week": second_week.isocalendar().week,
                 "provider_type": VCSProviders.BITBUCKET, "finding_count": 12}
        finding_counts = [data1, data2, data3]

        data = convert_rows_to_finding_count_over_time(finding_counts, weeks=3)
        assert len(data) == 3
        assert data[2].time_period == f"{first_week.isocalendar().year} W{first_week.isocalendar().week:02d}"
        assert data[2].vcs_provider_finding_count.AZURE_DEVOPS == data1["finding_count"]
        assert data[2].total == data1["finding_count"]
        assert data[1].time_period == f"{second_week.isocalendar().year} W{second_week.isocalendar().week:02d}"
        assert data[1].vcs_provider_finding_count.AZURE_DEVOPS == data2["finding_count"]
        assert data[1].vcs_provider_finding_count.BITBUCKET == data3["finding_count"]
        assert data[1].total == data2["finding_count"]+data3["finding_count"]
        assert data[0].time_period == f"{third_week.isocalendar().year} W{third_week.isocalendar().week:02d}"
        assert data[0].total == 0
