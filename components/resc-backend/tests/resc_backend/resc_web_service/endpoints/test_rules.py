# Standard Library
import json
import unittest
from typing import Generator
from unittest.mock import ANY, patch

# Third Party
import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# First Party
from resc_backend.constants import (
    CACHE_PREFIX,
    REDIS_CACHE_EXPIRE,
    RWS_ROUTE_DETECTED_RULES,
    RWS_ROUTE_FINDING_STATUS_COUNT,
    RWS_ROUTE_RULES,
    RWS_VERSION_PREFIX
)
from resc_backend.db.model import DBrule
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.cache_manager import CacheManager
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.rule import RuleCreate
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


class TestRules(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth

        self.db_rule_list = []
        for i in range(1, 6):
            self.db_rule_list.append(DBrule(
                rule_pack=f"1.0.{i}",
                allow_list=i,
                rule_name=f"rule_name_{i}",
                description=f"description_{i}",
                entropy=1.0,
                secret_group=i,
                regex=f"regex_{i}",
                path=f"path_{i}",
                keywords=f"keywords_{i}"))
            self.db_rule_list[i - 1].id_ = i

        self.db_rules = []
        for i in range(1, 6):
            self.db_rules.append(DBrule(rule_name=f"test{i}", rule_pack=f"rule_pack_{i}", description=f"descr{i}"))
            self.db_rules[i - 1].id_ = i

        self.db_status_count = []
        counter = 1
        for finding_status in FindingStatus:
            counter = counter + 1
            self.db_status_count.append((counter, finding_status))
        self.db_status_count = sorted(self.db_status_count, key=lambda status_count: status_count[1])

    @staticmethod
    def cast_db_rule_to_rule_create(rule: DBrule):
        return RuleCreate(rule_pack=rule.rule_pack,
                          allow_list=rule.allow_list,
                          rule_name=rule.rule_name,
                          description=rule.description,
                          entropy=rule.entropy,
                          secret_group=rule.secret_group,
                          regex=rule.regex,
                          path=rule.path,
                          keywords=rule.keywords
                          )

    @staticmethod
    def create_json_body_for_rule(rule: DBrule):
        return json.loads(TestRules.cast_db_rule_to_rule_create(rule).json())

    @staticmethod
    def assert_cache(cached_response):
        assert FastAPICache.get_enable() is True
        assert FastAPICache.get_prefix() == CACHE_PREFIX
        assert FastAPICache.get_expire() == REDIS_CACHE_EXPIRE
        assert FastAPICache.get_key_builder() is not None
        assert FastAPICache.get_coder() is not None
        assert cached_response.headers.get("cache-control") is not None

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_single_finding_status(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_multiple_finding_status(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}"
                                  f"&findingstatus={FindingStatus.CLARIFICATION_REQUIRED}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}"
                                         f"&findingstatus={FindingStatus.CLARIFICATION_REQUIRED}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_single_vcs_provider(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_multiple_vcs_provider(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}"
                                  f"&vcsprovider={VCSProviders.AZURE_DEVOPS}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}"
                                         f"&vcsprovider={VCSProviders.AZURE_DEVOPS}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_project_name(self, get_distinct_rules_from_findings):
        project_name = "Test_Project"
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?projectname={project_name}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?projectname={project_name}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_repository_name(self, get_distinct_rules_from_findings):
        repository_name = "Test_Repository"
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?repositoryname={repository_name}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?repositoryname={repository_name}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_start_date(self, get_distinct_rules_from_findings):
        start_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?start_date_time={start_date_time}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?start_date_time={start_date_time}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_end_date(self, get_distinct_rules_from_findings):
        end_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?end_date_time={end_date_time}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?end_date_time={end_date_time}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_rule_pack_version(self, get_distinct_rules_from_findings):
        rule_pack_version = "rule_pack_1"
        get_distinct_rules_from_findings.return_value = [self.db_rules[0]]
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?rule_pack_version={rule_pack_version}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 1
            assert data[0] == self.db_rules[0].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?rule_pack_version={rule_pack_version}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_when_all_filters_selected(self, get_distinct_rules_from_findings):
        project_name = "Test_Project"
        repository_name = "Test_Repository"
        start_date_time = "1991-07-01T00:00:00"
        end_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}"
                                  f"&vcsprovider={VCSProviders.BITBUCKET}"
                                  f"&projectname={project_name}"
                                  f"&repositoryname={repository_name}"
                                  f"&start_date_time={start_date_time}"
                                  f"&end_date_time={end_date_time}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}"
                                         f"&vcsprovider={VCSProviders.BITBUCKET}"
                                         f"&projectname={project_name}"
                                         f"&repositoryname={repository_name}"
                                         f"&start_date_time={start_date_time}"
                                         f"&end_date_time={end_date_time}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_when_no_filter_selected(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_DETECTED_RULES}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == len(self.db_rules)
            assert data[0] == self.db_rules[0].rule_name
            assert data[1] == self.db_rules[1].rule_name

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_DETECTED_RULES}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_rule_findings_count_by_status")
    def test_get_rules_finding_status_count(self, get_rule_findings_count_by_status):
        rule_statuses = {self.db_rules[0].rule_name: {
            "true_positive": 2,
            "false_positive": 2,
            "not_analyzed": 2,
            "under_review": 2,
            "clarification_required": 2,
            "total_findings_count": 10
        }}
        get_rule_findings_count_by_status.return_value = rule_statuses
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 1
            assert data[0]["rule_name"] == self.db_rules[0].rule_name
            assert data[0]["finding_count"] == 10
            assert len(data[0]["finding_statuses_count"]) == len(self.db_status_count)
            for status in range(len(self.db_status_count)):
                assert data[0]["finding_statuses_count"][status]["count"] == 2

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_rule_findings_count_by_status")
    def test_get_rules_finding_status_count_with_valid_rule_pack_filter(self, get_rule_findings_count_by_status):
        rule_pack_version = "1.0.1"
        rule_statuses = {self.db_rules[0].rule_name: {
            "true_positive": 2,
            "false_positive": 2,
            "not_analyzed": 2,
            "under_review": 2,
            "clarification_required": 2,
            "total_findings_count": 10
        }}
        get_rule_findings_count_by_status.return_value = rule_statuses
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                  f"?rule_pack_version={rule_pack_version}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 1
            assert data[0]["rule_name"] == self.db_rules[0].rule_name
            assert data[0]["finding_count"] == 10
            assert len(data[0]["finding_statuses_count"]) == len(self.db_status_count)
            for status in range(len(self.db_status_count)):
                assert data[0]["finding_statuses_count"][status]["count"] == 2

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                         f"?rule_pack_version={rule_pack_version}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_rule_findings_count_by_status")
    def test_get_rules_finding_status_count_with_multiple_rule_pack_filter(self, get_rule_findings_count_by_status):
        version1 = "1.0.1"
        version2 = "1.0.2"
        rule_statuses = {self.db_rules[0].rule_name: {
            "true_positive": 2,
            "false_positive": 2,
            "not_analyzed": 2,
            "under_review": 2,
            "clarification_required": 2,
            "total_findings_count": 10
        }}
        get_rule_findings_count_by_status.return_value = rule_statuses
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                  f"?rule_pack_version={version1}&rule_pack_version={version2}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 1
            assert data[0]["rule_name"] == self.db_rules[0].rule_name
            assert data[0]["finding_count"] == 10
            assert len(data[0]["finding_statuses_count"]) == len(self.db_status_count)
            for status in range(len(self.db_status_count)):
                assert data[0]["finding_statuses_count"][status]["count"] == 2

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                         f"?rule_pack_version={version1}&rule_pack_version={version2}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()

    @patch("resc_backend.resc_web_service.crud.finding.get_rule_findings_count_by_status")
    def test_get_rules_finding_status_count_with_invalid_rule_pack_filter(self, get_rule_findings_count_by_status):
        rule_pack_version = "invalid"
        rule_statuses = {}
        get_rule_findings_count_by_status.return_value = rule_statuses
        with self.client as client:
            response = client.get(f"{RWS_VERSION_PREFIX}"
                                  f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                  f"?rule_pack_version={rule_pack_version}")
            assert response.status_code == 200, response.text
            data = response.json()
            assert len(data) == 0
            assert data == []

            # Make the second request to retrieve response from cache
            cached_response = client.get(f"{RWS_VERSION_PREFIX}"
                                         f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}"
                                         f"?rule_pack_version={rule_pack_version}")
            self.assert_cache(cached_response)
            assert response.json() == cached_response.json()
