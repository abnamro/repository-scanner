# Standard Library
import json
import unittest
from unittest.mock import ANY, patch

# Third Party
from fastapi import HTTPException
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import RWS_ROUTE_RULE_PACKS, RWS_VERSION_PREFIX
from resc_backend.db.model.rule_allow_list import DBruleAllowList
from resc_backend.db.model.rule_pack import DBrulePack
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.endpoints.rule_packs import determine_uploaded_rule_pack_activation, read_rule_pack
from resc_backend.resc_web_service.schema.rule_pack import RulePackCreate


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

    @staticmethod
    def cast_db_rule_pack_to_rule_pack_create(rule_pack: DBrulePack):
        return RulePackCreate(version=rule_pack.version,
                              active=rule_pack.active,
                              global_allow_list=rule_pack.global_allow_list)

    @staticmethod
    def create_json_body_for_rule_pack(rule_pack: DBrulePack):
        return json.loads(TestRules.cast_db_rule_pack_to_rule_pack_create(rule_pack).json())

    @staticmethod
    def assert_rule_packs(data, rule_packs):
        assert data["version"] == rule_packs.version
        assert data["active"] == rule_packs.active
        assert data["global_allow_list"] == rule_packs.global_allow_list

    @patch("resc_backend.resc_web_service.crud.rule_pack.create_rule_pack_version")
    def test_create_rule_pack_version(self, create_rule_pack_version):
        db_rule_pack = self.db_rule_packs[0]
        create_rule_pack_version.return_value = db_rule_pack
        rule_pack = create_rule_pack_version(rule_pack=db_rule_pack, db_connection=ANY)

        assert rule_pack.version == self.db_rule_packs[0].version
        assert rule_pack.active == self.db_rule_packs[0].active
        assert rule_pack.global_allow_list == self.db_rule_packs[0].global_allow_list
        create_rule_pack_version.assert_called_once_with(db_connection=ANY, rule_pack=db_rule_pack)

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_pack")
    def test_get_rule_pack_version_when_version_provided(self, get_rule_pack):
        db_rule_pack = self.db_rule_packs[0]
        get_rule_pack.return_value = db_rule_pack
        input_rule_pack_version = "1.0.1"

        rule_pack = read_rule_pack(version=input_rule_pack_version, db_connection=ANY)
        assert rule_pack.version == self.db_rule_packs[0].version
        assert rule_pack.active == self.db_rule_packs[0].active
        assert rule_pack.global_allow_list == self.db_rule_packs[0].global_allow_list
        get_rule_pack.assert_called_once_with(version="1.0.1", db_connection=ANY)

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_pack")
    def test_get_rule_pack_version_when_version_not_provided(self, get_rule_pack):
        db_rule_pack = self.db_rule_packs[0]
        get_rule_pack.return_value = db_rule_pack
        rule_pack = read_rule_pack(db_connection=ANY)

        assert rule_pack.version == self.db_rule_packs[0].version
        assert rule_pack.active == self.db_rule_packs[0].active
        assert rule_pack.global_allow_list == self.db_rule_packs[0].global_allow_list
        get_rule_pack.assert_called_once_with(version=None, db_connection=ANY)

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_pack")
    def test_get_rule_pack_version_when_version_not_exists(self, get_rule_pack):
        get_rule_pack.return_value = None
        version = "999.999.999"

        rule_pack = read_rule_pack(version=version, db_connection=ANY)
        assert rule_pack is None
        get_rule_pack.assert_called_once_with(version=version, db_connection=ANY)

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_pack")
    def test_get_rule_pack_version_when_invalid_version_provided(self, get_rule_pack):
        version = "109"
        with self.assertRaises(HTTPException) as exc_info:
            read_rule_pack(version=version, db_connection=ANY)
        assert isinstance(exc_info.exception, HTTPException)
        assert exc_info.exception.status_code == 422
        assert exc_info.exception.detail == f"Version {version} is not a valid semantic version"

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_total_rule_packs_count")
    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_packs")
    def test_multiple_rule_pack_versions(self, get_rule_packs, get_total_rule_packs_count):
        get_rule_packs.return_value = self.db_rule_packs[:2]
        get_total_rule_packs_count.return_value = len(self.db_rule_packs[:2])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULE_PACKS}/versions",
                                   params={"skip": 0, "limit": 5})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 2
        self.assert_rule_packs(data["data"][0], self.db_rule_packs[0])
        self.assert_rule_packs(data["data"][1], self.db_rule_packs[1])
        assert data["total"] == 2
        assert data["limit"] == 5
        assert data["skip"] == 0

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_packs")
    def test_multiple_rule_pack_versions_with_negative_skip(self, get_rule_packs):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULE_PACKS}/versions",
                                   params={"skip": -1, "limit": 5})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "skip"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 0"
        get_rule_packs.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.rule_pack.get_rule_packs")
    def test_multiple_rule_pack_versions_with_negative_limit(self, get_rule_packs):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_RULE_PACKS}/versions",
                                   params={"skip": 0, "limit": -1})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "limit"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 1"
        get_rule_packs.assert_not_called()

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

    @patch("resc_backend.resc_web_service.crud.rule.create_rule_allow_list")
    def test_create_rule_allow_list(self, create_rule_allow_list):
        db_allow_list = self.db_rule_allow_list[0]
        create_rule_allow_list.return_value = db_allow_list

        rule_allow_list = create_rule_allow_list(rule_allow_list=db_allow_list, db_connection=ANY)

        assert rule_allow_list.id_ == db_allow_list.id_
        assert rule_allow_list.commits == db_allow_list.commits
        assert rule_allow_list.description == db_allow_list.description
        assert rule_allow_list.paths == db_allow_list.paths
        assert rule_allow_list.regexes == db_allow_list.regexes
        assert rule_allow_list.stop_words == db_allow_list.stop_words
        create_rule_allow_list.assert_called_once_with(db_connection=ANY, rule_allow_list=db_allow_list)