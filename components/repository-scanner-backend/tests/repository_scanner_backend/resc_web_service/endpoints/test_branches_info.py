# Standard Library
import json
import unittest
from datetime import datetime
from unittest.mock import ANY, patch

# Third Party
from fastapi.testclient import TestClient

# First Party
from repository_scanner_backend.constants import (
    RWS_ROUTE_BRANCHES_INFO,
    RWS_ROUTE_LAST_SCAN,
    RWS_ROUTE_SCANS,
    RWS_VERSION_PREFIX
)
from repository_scanner_backend.db.model import DBbranchInfo, DBscan
from repository_scanner_backend.resc_web_service.api import app
from repository_scanner_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from repository_scanner_backend.resc_web_service.schema.branch_info import BranchInfoCreate


class TestBranchesInfo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth
        self.db_branches_info = []
        for i in range(1, 6):
            self.db_branches_info.append(
                DBbranchInfo(repository_info_id=i, branch_id=f"branch_id_{i}", branch_name=f"branch_name_{i}",
                             last_scanned_commit=f"last_scanned_commit_{i}"))
            self.db_branches_info[i-1].id_ = i

        self.db_scans = []
        for i in range(1, 6):
            self.db_scans.append(DBscan(branch_info_id=i, scan_type="BASE",
                                        last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(),
                                        increment_number=0, rule_pack="1.3"))
            self.db_scans[i-1].id_ = i

    @staticmethod
    def create_json_body(branch_info):
        return json.loads(TestBranchesInfo.cast_db_branch_info_to_branch_info_create(branch_info).json())

    @staticmethod
    def cast_db_branch_info_to_branch_info_create(branch_info):
        return BranchInfoCreate(branch_id=branch_info.branch_id,
                                branch_name=branch_info.branch_name,
                                last_scanned_commit=branch_info.last_scanned_commit,
                                repository_info_id=branch_info.repository_info_id)

    @staticmethod
    def assert_branch_info(data, branch_info):
        assert data["branch_id"] == branch_info.branch_id
        assert data["branch_name"] == branch_info.branch_name
        assert data["last_scanned_commit"] == branch_info.last_scanned_commit
        assert data["repository_info_id"] == branch_info.repository_info_id
        assert data["id_"] == branch_info.id_

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_get_branches_info_non_existing(self, get_branch_info):
        branch_info_id = 999
        get_branch_info.return_value = None
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}")
        assert response.status_code == 404, response.text
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_get_branches_info(self, get_branch_info):
        branch_info_id = 1
        get_branch_info.return_value = self.db_branches_info[branch_info_id]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}")
        assert response.status_code == 200, response.text
        self.assert_branch_info(response.json(), self.db_branches_info[branch_info_id])
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.create_branch_info_if_not_exists")
    def test_post_branches_info(self, create_branch_info_if_not_exists):
        branch_info_id = 1
        create_branch_info_if_not_exists.return_value = self.db_branches_info[branch_info_id]
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}",
                                    json=self.create_json_body(self.db_branches_info[branch_info_id]))
        assert response.status_code == 201, response.text
        self.assert_branch_info(response.json(), self.db_branches_info[branch_info_id])
        create_branch_info_if_not_exists.assert_called_once()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.create_branch_info_if_not_exists")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.create_branch_info")
    def test_post_branches_info_no_body(self, create_branch_info, create_branch_info_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_branch_info.assert_not_called()
        create_branch_info_if_not_exists.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.create_branch_info_if_not_exists")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.create_branch_info")
    def test_post_branches_info_empty_body(self, create_branch_info, create_branch_info_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}", json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'branch_id']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][1]["loc"] == ['body', 'branch_name']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'last_scanned_commit']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'repository_info_id']
        assert data["detail"][3]["msg"] == "field required"
        create_branch_info.assert_not_called()
        create_branch_info_if_not_exists.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.update_branch_info")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_put_branches_info(self, get_branch_info, update_branch_info):
        branch_info_id = 1
        get_branch_info.return_value = self.db_branches_info[0]
        get_branch_info.return_value.id_ = branch_info_id
        update_branch_info.return_value = self.db_branches_info[branch_info_id]
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}",
            json=self.create_json_body(self.db_branches_info[branch_info_id]))
        assert response.status_code == 200, response.text
        self.assert_branch_info(response.json(), self.db_branches_info[branch_info_id])
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)
        update_branch_info.assert_called_once()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.update_branch_info")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_put_branches_info_empty_body(self, get_branch_info, update_branch_info):
        response = self.client.put(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/9999999999",
                                   json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'branch_id']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][1]["loc"] == ['body', 'branch_name']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'last_scanned_commit']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'repository_info_id']
        assert data["detail"][3]["msg"] == "field required"
        get_branch_info.assert_not_called()
        update_branch_info.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.update_branch_info")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_put_branches_non_existing(self, get_branch_info, update_branch_info):
        branch_info_id = 999
        get_branch_info.return_value = None
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}",
            json=self.create_json_body(self.db_branches_info[0]))
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "BranchInfo not found"
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)
        update_branch_info.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.delete_branch_info")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_delete_branches_info(self, get_branch_info, delete_branch_info):
        branch_info_id = 1
        get_branch_info.return_value = self.db_branches_info[branch_info_id]
        delete_branch_info.return_value = self.db_branches_info[branch_info_id]
        response = self.client.delete(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}")
        assert response.status_code == 200, response.text
        self.assert_branch_info(response.json(), self.db_branches_info[branch_info_id])
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)
        delete_branch_info.assert_called_once_with(ANY, branch_info_id)

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.delete_branch_info")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_delete_branches_info_non_existing(self, get_branch_info, delete_branch_info):
        branch_info_id = 999
        get_branch_info.return_value = None
        response = self.client.delete(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}")
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "BranchInfo not found"
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)
        delete_branch_info.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branches_info_count")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branches_info")
    def test_get_multiple_branches_info(self, get_branches_info, get_branches_count):
        get_branches_info.return_value = self.db_branches_info[:2]
        get_branches_count.return_value = len(self.db_branches_info[:2])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}",
                                   params={"skip": 0, "limit": 5})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 2
        self.assert_branch_info(data["data"][0], self.db_branches_info[0])
        self.assert_branch_info(data["data"][1], self.db_branches_info[1])
        assert data["total"] == 2
        assert data["limit"] == 5
        assert data["skip"] == 0
        get_branches_info.assert_called_once_with(ANY, skip=0, limit=5)

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branches_info")
    def test_get_multiple_branches_info_with_negative_skip(self, get_branches_info):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}",
                                   params={"skip": -1, "limit": 5})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "skip"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 0"
        get_branches_info.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branches_info")
    def test_get_multiple_branches_info_with_negative_limit(self, get_branches_info):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}",
                                   params={"skip": 0, "limit": -1})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "limit"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 1"
        get_branches_info.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.scan.get_scans_count")
    @patch("repository_scanner_backend.resc_web_service.crud.scan.get_scans")
    def test_get_branches_info_scans(self, get_scans, get_scans_count):
        get_scans.return_value = self.db_scans[:2]
        get_scans_count.return_value = len(self.db_scans[:2])
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/1{RWS_ROUTE_SCANS}/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['total'] == len(self.db_scans[:2])
        assert data['limit'] == 100
        assert data['skip'] == 0
        assert len(data["data"]) == len(self.db_scans[:2])
        assert data["data"][0]["id_"] == self.db_scans[0].id_
        assert data["data"][1]["id_"] == self.db_scans[1].id_

    @patch("repository_scanner_backend.resc_web_service.crud.scan.get_latest_scan_for_branch")
    def test_get_last_scan_for_branch(self, get_latest_scan_for_branch):
        get_latest_scan_for_branch.return_value = self.db_scans[0]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/1{RWS_ROUTE_LAST_SCAN}/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['scan_type'] == self.db_scans[0].scan_type
        assert data['last_scanned_commit'] == self.db_scans[0].last_scanned_commit
        assert data["branch_info_id"] == self.db_scans[0].branch_info_id
        assert data["id_"] == self.db_scans[0].id_

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_findings_metadata_by_branch_info_id")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_get_findings_metadata_for_branch(self, get_branch_info, get_findings_metadata_by_branch_info_id):
        branch_info_id = 1
        get_branch_info.return_value = self.db_branches_info[branch_info_id]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}")
        assert response.status_code == 200, response.text
        self.assert_branch_info(response.json(), self.db_branches_info[branch_info_id])
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)

        get_findings_metadata_by_branch_info_id.return_value = {"true_positive": 1, "false_positive": 2,
                                                                "not_analyzed": 3,
                                                                "under_review": 4, "clarification_required": 5,
                                                                "total_findings_count": 15}
        response = get_findings_metadata_by_branch_info_id.return_value
        assert response["true_positive"] == 1
        assert response["false_positive"] == 2
        assert response["not_analyzed"] == 3
        assert response["under_review"] == 4
        assert response["clarification_required"] == 5
        assert response["total_findings_count"] == 15

    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_findings_metadata_by_branch_info_id")
    @patch("repository_scanner_backend.resc_web_service.crud.branch_info.get_branch_info")
    def test_get_findings_metadata_for_branch_non_existing(self, get_branch_info,
                                                           get_findings_metadata_by_branch_info_id):
        branch_info_id = 999
        get_branch_info.return_value = None
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES_INFO}/{branch_info_id}",
            json=self.create_json_body(self.db_branches_info[0]))
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "BranchInfo not found"
        get_branch_info.assert_called_once_with(ANY, branch_info_id=branch_info_id)
        get_findings_metadata_by_branch_info_id.assert_not_called()
