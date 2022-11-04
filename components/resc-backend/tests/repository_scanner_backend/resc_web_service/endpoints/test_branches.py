# Standard Library
import json
import unittest
from datetime import datetime
from unittest.mock import ANY, patch

# Third Party
from fastapi.testclient import TestClient

# First Party
from resc_backend.constants import RWS_ROUTE_BRANCHES, RWS_ROUTE_LAST_SCAN, RWS_ROUTE_SCANS, RWS_VERSION_PREFIX
from resc_backend.db.model import DBbranch, DBscan
from resc_backend.resc_web_service.api import app
from resc_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from resc_backend.resc_web_service.schema.branch import BranchCreate


class TestBranches(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth
        self.db_branches = []
        for i in range(1, 6):
            self.db_branches.append(
                DBbranch(repository_id=i, branch_id=f"branch_id_{i}", branch_name=f"branch_name_{i}",
                         last_scanned_commit=f"last_scanned_commit_{i}"))
            self.db_branches[i - 1].id_ = i

        self.db_scans = []
        for i in range(1, 6):
            self.db_scans.append(DBscan(branch_id=i, scan_type="BASE",
                                        last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(),
                                        increment_number=0, rule_pack="1.3"))
            self.db_scans[i - 1].id_ = i

    @staticmethod
    def create_json_body(branch):
        return json.loads(TestBranches.cast_db_branch_to_branch_create(branch).json())

    @staticmethod
    def cast_db_branch_to_branch_create(branch):
        return BranchCreate(branch_id=branch.branch_id,
                            branch_name=branch.branch_name,
                            last_scanned_commit=branch.last_scanned_commit,
                            repository_id=branch.repository_id)

    @staticmethod
    def assert_branch(data, branch):
        assert data["branch_id"] == branch.branch_id
        assert data["branch_name"] == branch.branch_name
        assert data["last_scanned_commit"] == branch.last_scanned_commit
        assert data["repository_id"] == branch.repository_id
        assert data["id_"] == branch.id_

    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_get_branches_non_existing(self, get_branch):
        branch_id = 999
        get_branch.return_value = None
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}")
        assert response.status_code == 404, response.text
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)

    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_get_branches(self, get_branch):
        branch_id = 1
        get_branch.return_value = self.db_branches[branch_id]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}")
        assert response.status_code == 200, response.text
        self.assert_branch(response.json(), self.db_branches[branch_id])
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)

    @patch("resc_backend.resc_web_service.crud.branch.create_branch_if_not_exists")
    def test_post_branches(self, create_branch_if_not_exists):
        branch_id = 1
        create_branch_if_not_exists.return_value = self.db_branches[branch_id]
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}",
                                    json=self.create_json_body(self.db_branches[branch_id]))
        assert response.status_code == 201, response.text
        self.assert_branch(response.json(), self.db_branches[branch_id])
        create_branch_if_not_exists.assert_called_once()

    @patch("resc_backend.resc_web_service.crud.branch.create_branch_if_not_exists")
    @patch("resc_backend.resc_web_service.crud.branch.create_branch")
    def test_post_branches_no_body(self, create_branch, create_branch_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}")
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_branch.assert_not_called()
        create_branch_if_not_exists.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.create_branch_if_not_exists")
    @patch("resc_backend.resc_web_service.crud.branch.create_branch")
    def test_post_branches_empty_body(self, create_branch, create_branch_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}", json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'branch_id']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][1]["loc"] == ['body', 'branch_name']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'last_scanned_commit']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'repository_id']
        assert data["detail"][3]["msg"] == "field required"
        create_branch.assert_not_called()
        create_branch_if_not_exists.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.update_branch")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_put_branches(self, get_branch, update_branch):
        branch_id = 1
        get_branch.return_value = self.db_branches[0]
        get_branch.return_value.id_ = branch_id
        update_branch.return_value = self.db_branches[branch_id]
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}",
            json=self.create_json_body(self.db_branches[branch_id]))
        assert response.status_code == 200, response.text
        self.assert_branch(response.json(), self.db_branches[branch_id])
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)
        update_branch.assert_called_once()

    @patch("resc_backend.resc_web_service.crud.branch.update_branch")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_put_branches_empty_body(self, get_branch, update_branch):
        response = self.client.put(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/9999999999",
                                   json={})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'branch_id']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][1]["loc"] == ['body', 'branch_name']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'last_scanned_commit']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'repository_id']
        assert data["detail"][3]["msg"] == "field required"
        get_branch.assert_not_called()
        update_branch.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.update_branch")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_put_branches_non_existing(self, get_branch, update_branch):
        branch_id = 999
        get_branch.return_value = None
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}",
            json=self.create_json_body(self.db_branches[0]))
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Branch not found"
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)
        update_branch.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.delete_branch")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_delete_branches(self, get_branch, delete_branch):
        branch_id = 1
        get_branch.return_value = self.db_branches[branch_id]
        response = self.client.delete(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}")
        assert response.status_code == 200, response.text
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)
        delete_branch.assert_called_once_with(ANY, branch_id=branch_id, delete_related=True)

    @patch("resc_backend.resc_web_service.crud.branch.delete_branch")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_delete_branches_non_existing(self, get_branch, delete_branch):
        branch_id = 999
        get_branch.return_value = None
        response = self.client.delete(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}")
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Branch not found"
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)
        delete_branch.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.get_branches_count")
    @patch("resc_backend.resc_web_service.crud.branch.get_branches")
    def test_get_multiple_branches(self, get_branches, get_branches_count):
        get_branches.return_value = self.db_branches[:2]
        get_branches_count.return_value = len(self.db_branches[:2])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}",
                                   params={"skip": 0, "limit": 5})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 2
        self.assert_branch(data["data"][0], self.db_branches[0])
        self.assert_branch(data["data"][1], self.db_branches[1])
        assert data["total"] == 2
        assert data["limit"] == 5
        assert data["skip"] == 0
        get_branches.assert_called_once_with(ANY, skip=0, limit=5)

    @patch("resc_backend.resc_web_service.crud.branch.get_branches")
    def test_get_multiple_branches_with_negative_skip(self, get_branches):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}",
                                   params={"skip": -1, "limit": 5})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "skip"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 0"
        get_branches.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.branch.get_branches")
    def test_get_multiple_branches_with_negative_limit(self, get_branches):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}",
                                   params={"skip": 0, "limit": -1})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "limit"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 1"
        get_branches.assert_not_called()

    @patch("resc_backend.resc_web_service.crud.scan.get_scans_count")
    @patch("resc_backend.resc_web_service.crud.scan.get_scans")
    def test_get_branches_scans(self, get_scans, get_scans_count):
        get_scans.return_value = self.db_scans[:2]
        get_scans_count.return_value = len(self.db_scans[:2])
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/1{RWS_ROUTE_SCANS}/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['total'] == len(self.db_scans[:2])
        assert data['limit'] == 100
        assert data['skip'] == 0
        assert len(data["data"]) == len(self.db_scans[:2])
        assert data["data"][0]["id_"] == self.db_scans[0].id_
        assert data["data"][1]["id_"] == self.db_scans[1].id_

    @patch("resc_backend.resc_web_service.crud.scan.get_latest_scan_for_branch")
    def test_get_last_scan_for_branch(self, get_latest_scan_for_branch):
        get_latest_scan_for_branch.return_value = self.db_scans[0]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/1{RWS_ROUTE_LAST_SCAN}/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['scan_type'] == self.db_scans[0].scan_type
        assert data['last_scanned_commit'] == self.db_scans[0].last_scanned_commit
        assert data["branch_id"] == self.db_scans[0].branch_id
        assert data["id_"] == self.db_scans[0].id_

    @patch("resc_backend.resc_web_service.crud.branch.get_findings_metadata_by_branch_id")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_get_findings_metadata_for_branch(self, get_branch, get_findings_metadata_by_branch_id):
        branch_id = 1
        get_branch.return_value = self.db_branches[branch_id]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}")
        assert response.status_code == 200, response.text
        self.assert_branch(response.json(), self.db_branches[branch_id])
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)

        get_findings_metadata_by_branch_id.return_value = {"true_positive": 1, "false_positive": 2,
                                                           "not_analyzed": 3,
                                                           "under_review": 4, "clarification_required": 5,
                                                           "total_findings_count": 15}
        response = get_findings_metadata_by_branch_id.return_value
        assert response["true_positive"] == 1
        assert response["false_positive"] == 2
        assert response["not_analyzed"] == 3
        assert response["under_review"] == 4
        assert response["clarification_required"] == 5
        assert response["total_findings_count"] == 15

    @patch("resc_backend.resc_web_service.crud.branch.get_findings_metadata_by_branch_id")
    @patch("resc_backend.resc_web_service.crud.branch.get_branch")
    def test_get_findings_metadata_for_branch_non_existing(self, get_branch,
                                                           get_findings_metadata_by_branch_id):
        branch_id = 999
        get_branch.return_value = None
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_BRANCHES}/{branch_id}",
            json=self.create_json_body(self.db_branches[0]))
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Branch not found"
        get_branch.assert_called_once_with(ANY, branch_id=branch_id)
        get_findings_metadata_by_branch_id.assert_not_called()
