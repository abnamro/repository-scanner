# Standard Library
import json
import unittest
from unittest.mock import ANY, patch

# Third Party
from fastapi.testclient import TestClient

# First Party
from repository_scanner_backend.constants import RWS_ROUTE_VCS, RWS_VERSION_PREFIX
from repository_scanner_backend.db.model import DBVcsInstance
from repository_scanner_backend.resc_web_service.api import app
from repository_scanner_backend.resc_web_service.dependencies import requires_auth, requires_no_auth
from repository_scanner_backend.resc_web_service.schema.vcs_instance import VCSInstanceCreate


class TestVCSInstances(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[requires_auth] = requires_no_auth
        self.db_vcs_instances = []
        for i in range(1, 6):
            self.db_vcs_instances.append(DBVcsInstance(name=f"name_{i}",
                                                       provider_type="BITBUCKET",
                                                       hostname="hostname",
                                                       port=i,
                                                       scheme="https",
                                                       exceptions=[],
                                                       scope=[],
                                                       organization="organization"))
            self.db_vcs_instances[i - 1].id_ = i

    @staticmethod
    def cast_db_vcs_instance_to_vcs_instance_create(vcs_instance: DBVcsInstance):
        return VCSInstanceCreate(name=vcs_instance.name,
                                 provider_type=vcs_instance.provider_type,
                                 hostname=vcs_instance.hostname,
                                 port=vcs_instance.port,
                                 scheme=vcs_instance.scheme,
                                 exceptions=vcs_instance.exceptions,
                                 scope=vcs_instance.scope)

    @staticmethod
    def create_json_body(vcs_instance: DBVcsInstance):
        return json.loads(TestVCSInstances.cast_db_vcs_instance_to_vcs_instance_create(vcs_instance).json())

    @staticmethod
    def assert_vcs_instance(data, vcs_instance):
        assert data["id_"] == vcs_instance.id_
        assert data["name"] == vcs_instance.name
        assert data["provider_type"] == vcs_instance.provider_type
        assert data["hostname"] == vcs_instance.hostname
        assert data["port"] == vcs_instance.port
        assert data["scheme"] == vcs_instance.scheme
        assert data["exceptions"] == vcs_instance.exceptions
        assert data["scope"] == vcs_instance.scope
        assert data["organization"] == vcs_instance.organization

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.create_vcs_instance_if_not_exists")
    def test_post_vcs_instance(self, create_vcs_instance_if_not_exists):
        db_vcs_instance = self.db_vcs_instances[0]
        create_vcs_instance_if_not_exists.return_value = db_vcs_instance
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                    json=self.create_json_body(db_vcs_instance))

        assert response.status_code == 201, response.text
        self.assert_vcs_instance(response.json(), db_vcs_instance)
        create_vcs_instance_if_not_exists \
            .assert_called_once_with(db_connection=ANY,
                                     vcs_instance=self.cast_db_vcs_instance_to_vcs_instance_create(
                                         db_vcs_instance))

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.create_vcs_instance_if_not_exists")
    def test_post_vcs_instance_no_body(self, create_vcs_instance_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}")

        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert data["detail"][0]["msg"] == "field required"
        create_vcs_instance_if_not_exists.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.create_vcs_instance_if_not_exists")
    def test_post_vcs_instance_empty_body(self, create_vcs_instance_if_not_exists):
        response = self.client.post(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}", json={})

        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'name']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][0]["type"] == "value_error.missing"
        assert data["detail"][1]["loc"] == ['body', 'provider_type']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'hostname']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'port']
        assert data["detail"][3]["msg"] == "field required"
        assert data["detail"][3]["msg"] == "field required"
        assert data["detail"][4]["loc"] == ['body', 'scheme']
        assert data["detail"][4]["msg"] == "field required"
        assert data["detail"][4]["msg"] == "field required"
        create_vcs_instance_if_not_exists.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    def test_read_vcs_instance(self, read_vcs_instance):
        vcs_instance_id = 1
        read_vcs_instance.return_value = self.db_vcs_instances[vcs_instance_id]
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}/{vcs_instance_id}")
        assert response.status_code == 200, response.text
        self.assert_vcs_instance(response.json(), self.db_vcs_instances[vcs_instance_id])
        read_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    def test_read_vcs_instance_non_existing(self, read_vcs_instance):
        vcs_instance_id = 999
        read_vcs_instance.return_value = None
        response = self.client.get(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}/{vcs_instance_id}")
        assert response.status_code == 404, response.text
        read_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances_count")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances(self, get_vcs_instances, get_vcs_instances_count):
        get_vcs_instances.return_value = self.db_vcs_instances[:2]
        get_vcs_instances_count.return_value = len(self.db_vcs_instances[:2])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": 0, "limit": 5})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 2
        self.assert_vcs_instance(data["data"][0], self.db_vcs_instances[0])
        self.assert_vcs_instance(data["data"][1], self.db_vcs_instances[1])
        assert data["total"] == 2
        assert data["limit"] == 5
        assert data["skip"] == 0

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances_with_negative_skip(self, get_vcs_instances):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": -1, "limit": 5})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "skip"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 0"
        get_vcs_instances.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances_with_negative_limit(self, get_vcs_instances):
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": 0, "limit": -1})
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ["query", "limit"]
        assert data["detail"][0]["msg"] == "ensure this value is greater than or equal to 1"
        get_vcs_instances.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances_count")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances_with_vcs_provider_type_filter(self, get_vcs_instances, get_vcs_instances_count):
        get_vcs_instances.return_value = self.db_vcs_instances[:5]
        get_vcs_instances_count.return_value = len(self.db_vcs_instances[:5])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": 0, "limit": 5, "vcs_provider_type": "BITBUCKET"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 5
        self.assert_vcs_instance(data["data"][0], self.db_vcs_instances[0])
        self.assert_vcs_instance(data["data"][1], self.db_vcs_instances[1])
        self.assert_vcs_instance(data["data"][2], self.db_vcs_instances[2])
        self.assert_vcs_instance(data["data"][3], self.db_vcs_instances[3])
        self.assert_vcs_instance(data["data"][4], self.db_vcs_instances[4])
        assert data["total"] == 5
        assert data["limit"] == 5
        assert data["skip"] == 0

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances_count")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances_with_vcs_instance_name_filter(self, get_vcs_instances, get_vcs_instances_count):
        get_vcs_instances.return_value = self.db_vcs_instances[:1]
        get_vcs_instances_count.return_value = len(self.db_vcs_instances[:1])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": 0, "limit": 1, "vcs_instance_name": "name_1"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 1
        self.assert_vcs_instance(data["data"][0], self.db_vcs_instances[0])
        assert data["total"] == 1
        assert data["limit"] == 1
        assert data["skip"] == 0

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances_count")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instances")
    def test_get_all_vcs_instances_with_vcs_provider_type_and_vcs_instance_name_filter(self, get_vcs_instances,
                                                                                       get_vcs_instances_count):
        get_vcs_instances.return_value = self.db_vcs_instances[:1]
        get_vcs_instances_count.return_value = len(self.db_vcs_instances[:1])
        response = self.client.get(f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}",
                                   params={"skip": 0, "limit": 1, "vcs_provider_type": "BITBUCKET",
                                           "vcs_instance_name": "name_1"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["data"]) == 1
        self.assert_vcs_instance(data["data"][0], self.db_vcs_instances[0])
        assert data["total"] == 1
        assert data["limit"] == 1
        assert data["skip"] == 0

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.update_vcs_instance")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    def test_update_vcs_instance(self, get_vcs_instance, update_vcs_instance):
        vcs_instance_id = 1
        get_vcs_instance.return_value = self.db_vcs_instances[vcs_instance_id]
        update_vcs_instance.return_value = self.db_vcs_instances[1]
        update_vcs_instance.return_value.id_ = get_vcs_instance.return_value.id_
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}/{vcs_instance_id}",
            json=self.create_json_body(self.db_vcs_instances[1]))
        assert response.status_code == 200, response.text
        self.assert_vcs_instance(response.json(), self.db_vcs_instances[1])
        get_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)
        update_vcs_instance \
            .assert_called_once_with(db_connection=ANY,
                                     vcs_instance=self.cast_db_vcs_instance_to_vcs_instance_create(
                                         self.db_vcs_instances[1]), vcs_instance_id=vcs_instance_id)

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.update_vcs_instance")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    def test_update_vcs_instance_empty_body(self, update_vcs_instance, get_vcs_instance):
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}/9999999999", json={}, )
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"][0]["loc"] == ['body', 'name']
        assert data["detail"][0]["msg"] == "field required"
        assert data["detail"][0]["type"] == "value_error.missing"
        assert data["detail"][1]["loc"] == ['body', 'provider_type']
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][1]["msg"] == "field required"
        assert data["detail"][2]["loc"] == ['body', 'hostname']
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][2]["msg"] == "field required"
        assert data["detail"][3]["loc"] == ['body', 'port']
        assert data["detail"][3]["msg"] == "field required"
        assert data["detail"][3]["msg"] == "field required"
        assert data["detail"][4]["loc"] == ['body', 'scheme']
        assert data["detail"][4]["msg"] == "field required"
        assert data["detail"][4]["msg"] == "field required"
        update_vcs_instance.assert_not_called()
        get_vcs_instance.assert_not_called()

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.update_vcs_instance")
    def test_update_vcs_instance_non_existing(self, update_vcs_instance, get_vcs_instance):
        vcs_instance_id = 999
        get_vcs_instance.return_value = None
        response = self.client.put(
            f"{RWS_VERSION_PREFIX}{RWS_ROUTE_VCS}/{vcs_instance_id}",
            json={"name": "updated_name",
                  "provider_type": "BITBUCKET",
                  "hostname": "updated_host",
                  "port": 443,
                  "scheme": "https"
                  },
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "VCS instance not found"
        update_vcs_instance.assert_not_called()
        get_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.delete_vcs_instance")
    def test_delete_vcs_instance(self, delete_vcs_instance, get_vcs_instance):
        vcs_instance_id = 1
        get_vcs_instance.return_value = self.db_vcs_instances[vcs_instance_id]
        delete_vcs_instance.return_value = get_vcs_instance.return_value
        response = self.client.delete(f"{RWS_VERSION_PREFIX}"
                                      f"{RWS_ROUTE_VCS}/{vcs_instance_id}")
        assert response.status_code == 200, response.text
        self.assert_vcs_instance(response.json(), self.db_vcs_instances[vcs_instance_id])
        get_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)
        delete_vcs_instance.assert_called_once_with(ANY, vcs_instance_id)

    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.get_vcs_instance")
    @patch("repository_scanner_backend.resc_web_service.crud.vcs_instance.delete_vcs_instance")
    def test_delete_vcs_instance_invalid(self, delete_vcs_instance, get_vcs_instance):
        vcs_instance_id = 999
        get_vcs_instance.return_value = None
        response = self.client.delete(f"{RWS_VERSION_PREFIX}"
                                      f"{RWS_ROUTE_VCS}/{vcs_instance_id}")
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "VCS instance not found"
        delete_vcs_instance.assert_not_called()
        get_vcs_instance.assert_called_once_with(ANY, vcs_instance_id=vcs_instance_id)
