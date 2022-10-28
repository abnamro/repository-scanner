# Standard Library
import json
import unittest
from unittest.mock import ANY, patch

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import (
    RWS_ROUTE_DETECTED_RULES,
    RWS_ROUTE_FINDING_STATUS_COUNT,
    RWS_ROUTE_RULE_ALLOW_LIST,
    RWS_ROUTE_RULE_PACK,
    RWS_ROUTE_RULE_PACKS,
    RWS_ROUTE_RULES,
    RWS_VERSION_PREFIX
)
from resc_backend.db.model import DBrule
from resc_backend.db.model.rule_allow_list import DBruleAllowList
from resc_backend.db.model.rule_pack import DBrulePack
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.endpoints.rules import determine_uploaded_rule_pack_activation
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.rule import RuleCreate
from resc_backend.resc_web_service.schema.rule_allow_list import RuleAllowListCreate
from resc_backend.resc_web_service.schema.rule_pack import RulePackCreate
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


class TestRules(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth
        self.db_rule_allow_list = []
        for i in range(1, 6):
            self.db_rule_allow_list.append(DBruleAllowList(
                description=f"description_{i}",
                regexes=f"regexes_{i}",
                paths=f"paths_{i}",
                commits=f"commits_{i}",
                stop_words=f"stop_words_{i}"))
            self.db_rule_allow_list[i - 1].id_ = i

        self.db_rule_packs = []
        for i in range(1, 6):
            self.db_rule_packs.append(DBrulePack(
                version=f"1.0.{i}",
                active=False,
                global_allow_list=i))

        self.db_rule_list = []
        for i in range(1, 6):
            self.db_rule_list.append(DBrule(
                rule_pack=f"1.0.{i}",
                allow_list=i,
                rule_name=f"rule_name_{i}",
                description=f"description_{i}",
                tags=f"tags_{i}",
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
            self.db_status_count.append((finding_status, counter))
        self.db_status_count = sorted(self.db_status_count, key=lambda status_count: status_count[0])

    @staticmethod
    def cast_allow_list_to_allow_list_create(rule_allow_list: DBruleAllowList):
        return RuleAllowListCreate(description=rule_allow_list.description,
                                   regexes=rule_allow_list.regexes,
                                   paths=rule_allow_list.paths,
                                   commits=rule_allow_list.commits,
                                   stop_words=rule_allow_list.stop_words)

    @staticmethod
    def create_json_body_for_rule_allow_list(rule_allow_list: DBruleAllowList):
        return json.loads(TestRules.cast_allow_list_to_allow_list_create(rule_allow_list).json())

    @staticmethod
    def cast_db_rule_pack_to_rule_pack_create(rule_pack: DBrulePack):
        return RulePackCreate(version=rule_pack.version,
                              active=rule_pack.active,
                              global_allow_list=rule_pack.global_allow_list)

    @staticmethod
    def create_json_body_for_rule_pack(rule_pack: DBrulePack):
        return json.loads(TestRules.cast_db_rule_pack_to_rule_pack_create(rule_pack).json())

    @staticmethod
    def cast_db_rule_to_rule_create(rule: DBrule):
        return RuleCreate(rule_pack=rule.rule_pack,
                          allow_list=rule.allow_list,
                          rule_name=rule.rule_name,
                          description=rule.description,
                          tags=rule.tags,
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
    def assert_rule_packs(data, rule_packs):
        assert data["version"] == rule_packs.version
        assert data["active"] == rule_packs.active
        assert data["global_allow_list"] == rule_packs.global_allow_list

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_single_finding_status(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_multiple_finding_status(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?findingstatus={FindingStatus.NOT_ANALYZED}"
                                   f"&findingstatus={FindingStatus.CLARIFICATION_REQUIRED}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_single_vcs_provider(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_multiple_vcs_provider(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?vcsprovider={VCSProviders.BITBUCKET}"
                                   f"&vcsprovider={VCSProviders.AZURE_DEVOPS}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_project_name(self, get_distinct_rules_from_findings):
        project_name = "Test_Project"
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?projectname={project_name}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_repository_name(self, get_distinct_rules_from_findings):
        repository_name = "Test_Repository"
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?repositoryname={repository_name}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_start_date(self, get_distinct_rules_from_findings):
        start_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?start_date_time={start_date_time}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_by_end_date(self, get_distinct_rules_from_findings):
        end_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}?end_date_time={end_date_time}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_when_all_filters_selected(self, get_distinct_rules_from_findings):
        project_name = "Test_Project"
        repository_name = "Test_Repository"
        start_date_time = "1991-07-01T00:00:00"
        end_date_time = "1991-07-01T00:00:00"
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
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

    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_distinct_rules_from_findings_when_no_filter_selected(self, get_distinct_rules_from_findings):
        get_distinct_rules_from_findings.return_value = self.db_rules
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_DETECTED_RULES}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        assert data[0] == self.db_rules[0].rule_name
        assert data[1] == self.db_rules[1].rule_name

    @patch("resc_backend.resc_web_service.crud.finding.get_findings_count_by_status")
    @patch("resc_backend.resc_web_service.crud.finding.get_distinct_rules_from_findings")
    def test_get_get_rules_finding_status_count(self, get_distinct_rules_from_findings, get_findings_count_by_status):
        get_distinct_rules_from_findings.return_value = self.db_rules
        get_findings_count_by_status.return_value = self.db_status_count
        response = self.client.get(f"{RWS_VERSION_PREFIX}"
                                   f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == len(self.db_rules)
        for i in range(len(self.db_rules)):
            assert data[i]["rule_name"] == self.db_rules[i].rule_name
            assert data[i]["finding_count"] == 20
            assert len(data[i]["finding_statuses_count"]) == len(self.db_status_count)
            for status in range(len(self.db_status_count)):
                assert data[i]["finding_statuses_count"][status]["status"] == self.db_status_count[status][0]
                assert data[i]["finding_statuses_count"][status]["count"] == self.db_status_count[status][1]

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_allow_list")
    def test_post_rule_allow_list(self, create_rule_allow_list):
        db_allow_list = self.db_rule_allow_list[0]
        create_rule_allow_list.return_value = db_allow_list
        input_json = self.create_json_body_for_rule_allow_list(db_allow_list)
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_ALLOW_LIST}",
                                    json=input_json)
        assert response.status_code == 201, response.text
        create_rule_allow_list.assert_called_once_with(db_connection=ANY,
                                                       rule_allow_list=self.cast_allow_list_to_allow_list_create(
                                                           db_allow_list))

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_allow_list")
    def test_post_rule_allow_list_no_body(self, create_rule_allow_list):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_ALLOW_LIST}")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_rule_allow_list.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_allow_list")
    def test_post_rule_allow_list_empty_body(self, create_rule_allow_list):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_ALLOW_LIST}",
                                    json={})
        assert response.status_code == 400, response.text
        data = response.json()
        assert data["detail"] == 'No properties defined for rule allow list'
        create_rule_allow_list.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_pack_version")
    def test_post_rule_pack(self, create_rule_pack_version):
        db_rule_pack = self.db_rule_packs[0]
        create_rule_pack_version.return_value = db_rule_pack
        input_json = self.create_json_body_for_rule_pack(db_rule_pack)
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}",
                                    json=input_json)
        assert response.status_code == 201, response.text
        create_rule_pack_version.assert_called_once_with(db_connection=ANY,
                                                         rule_pack=self.cast_db_rule_pack_to_rule_pack_create(
                                                             db_rule_pack))

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_pack_version")
    def test_post_rule_pack_no_body(self, create_rule_pack_version):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_rule_pack_version.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_pack_version")
    def test_post_rule_pack_empty_body(self, create_rule_pack_version):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}",
                                    json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'version']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][0]["type"] == "value_error.missing"
        create_rule_pack_version.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.create_rule")
    def test_post_rule(self, create_rule):
        db_rule = self.db_rule_list[0]
        create_rule.return_value = db_rule
        input_json = self.create_json_body_for_rule(db_rule)
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}",
                                    json=input_json)
        assert response.status_code == 201, response.text
        create_rule.assert_called_once_with(db_connection=ANY,
                                            rule=self.cast_db_rule_to_rule_create(db_rule))

    @patch("resc_backend.resc_web_service.crud.rule.create_rule")
    def test_post_rule_no_body(self, create_rule):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_rule.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.create_rule")
    def test_post_rule_empty_body(self, create_rule):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}",
                                    json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'rule_name']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][0]["type"] == "value_error.missing"
        assert data["detail"][1]["loc"] == ['body', 'rule_pack']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][1]["type"] == "value_error.missing"
        create_rule.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.get_rule_pack")
    def test_get_rule_pack_version_when_version_provided(self, get_rule_pack):
        db_rule_pack = self.db_rule_packs[0]
        get_rule_pack.return_value = db_rule_pack
        input_rule_pack_version = "1.0.1"
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}"
                                   f"?version={input_rule_pack_version}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["version"] == self.db_rule_packs[0].version
        assert data["active"] == self.db_rule_packs[0].active
        assert data["global_allow_list"] == self.db_rule_packs[0].global_allow_list

    @patch("resc_backend.resc_web_service.crud.rule.get_rule_pack")
    def test_get_rule_pack_version_when_version_not_provided(self, get_rule_pack):
        db_rule_pack = self.db_rule_packs[0]
        get_rule_pack.return_value = db_rule_pack
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["version"] == self.db_rule_packs[0].version
        assert data["active"] == self.db_rule_packs[0].active
        assert data["global_allow_list"] == self.db_rule_packs[0].global_allow_list

    @patch("resc_backend.resc_web_service.crud.rule.get_rule_pack")
    def test_get_rule_pack_version_when_version_not_exists(self, get_rule_pack):
        get_rule_pack.return_value = None
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}"
                                   f"?version=999.999.999")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data is None

    @patch("resc_backend.resc_web_service.crud.rule.get_rule_pack")
    def test_get_rule_pack_version_when_invalid_version_provided(self, get_rule_pack):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}"
                                   f"?version=not_exists")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"][1] == "version"
        assert data["detail"][0]["msg"] == 'string does not match regex "^\\d+(?:\\.\\d+){2}$"'
        assert data["detail"][0]["type"] == "value_error.str.regex"
        get_rule_pack.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.get_rule_packs_count")
    @patch("resc_backend.resc_web_service.crud.rule.get_all_rule_packs")
    def test_multiple_rule_pack_versions(self, get_all_rule_packs, get_rule_packs_count):
        get_all_rule_packs.return_value = self.db_rule_packs[:2]
        get_rule_packs_count.return_value = len(self.db_rule_packs[:2])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACKS}",
                                   params={"skip": 0, "limit": 5})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 2
        self.assert_rule_packs(data["data"][0], self.db_rule_packs[0])
        self.assert_rule_packs(data["data"][1], self.db_rule_packs[1])
        assert data["total"] == 2
        assert data["limit"] == 5
        assert data["skip"] == 0

    @patch("resc_backend.resc_web_service.crud.rule.get_all_rule_packs")
    def test_multiple_rule_pack_versions_with_negative_skip(self, get_all_rule_pack_versions):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACKS}",
                                   params={"skip": -1, "limit": 5})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "skip"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 0"
        get_all_rule_pack_versions.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule.get_all_rule_packs")
    def test_multiple_rule_pack_versions_with_negative_limit(self, get_all_rule_pack_versions):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACKS}",
                                   params={"skip": 0, "limit": -1})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "limit"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 1"
        get_all_rule_pack_versions.assert_not_called()

    @patch('logging.Logger.info')
    def test_rule_pack_activation_when_requested_rule_pack_version_is_greater_than_latest_rule_pack_from_db(self, mock):
        db_rule_pack = self.db_rule_packs[0]
        latest_rule_pack_from_db = db_rule_pack
        requested_rule_pack_version = "1.0.2"
        activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(requested_rule_pack_version,
                                                                              latest_rule_pack_from_db)
        assert activate_uploaded_rule_pack is True
        mock.assert_called_with(
            f"Uploaded rule pack is of version '{requested_rule_pack_version}', using it to replace "
            f"'{latest_rule_pack_from_db.version}' as the active one.")

    @patch('logging.Logger.info')
    def test_rule_pack_activation_when_no_rule_pack_present_in_db(self, mock):
        latest_rule_pack_from_db = None
        requested_rule_pack_version = "1.0.2"
        activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(requested_rule_pack_version,
                                                                              latest_rule_pack_from_db)
        assert activate_uploaded_rule_pack is True
        mock.assert_called_with(
            f"No existing rule pack found, So activating the uploaded rule pack '{requested_rule_pack_version}'")

    @patch('logging.Logger.info')
    def test_rule_pack_activation_when_latest_rule_pack_from_db_is_greater_and_latest_rule_pack_from_db_is_inactive(
            self, mock):
        db_rule_pack = self.db_rule_packs[0]
        latest_rule_pack_from_db = db_rule_pack
        requested_rule_pack_version = "1.0.0"
        activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(requested_rule_pack_version,
                                                                              latest_rule_pack_from_db)
        assert activate_uploaded_rule_pack is True
        mock.assert_called_with(
            f"There is already a more recent rule pack present in the database "
            f"'{latest_rule_pack_from_db.version}', but it is set to inactive. "
            f"Activating the uploaded rule pack '{requested_rule_pack_version}'")

    @patch('logging.Logger.info')
    def test_rule_pack_activation_when_latest_rule_pack_from_db_is_greater_and_latest_rule_pack_from_db_is_active(self,
                                                                                                                  mock):
        db_rule_pack = DBrulePack(version="1.0.1", active=True, global_allow_list=1)
        latest_rule_pack_from_db = db_rule_pack
        requested_rule_pack_version = "1.0.0"
        activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(requested_rule_pack_version,
                                                                              latest_rule_pack_from_db)
        assert activate_uploaded_rule_pack is False
        mock.assert_called_with(
            f"Uploaded rule pack is of version '{requested_rule_pack_version}', the existing rule pack "
            f"'{latest_rule_pack_from_db.version}' is kept as the active one.")
