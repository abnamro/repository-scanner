# Standard Library
from datetime import datetime

# Third Party
import pydantic
import pytest

# First Party
from repository_scanner_backend.db.model import DBfinding
from repository_scanner_backend.resc_web_service.schema.finding import FindingRead
from repository_scanner_backend.resc_web_service.schema.finding_status import FindingStatus
from repository_scanner_backend.resc_web_service.schema.pagination_model import PaginationModel


def test_pagination_model_int():
    int_list = []
    for i in range(1, 6):
        int_list.append(i)

    total = 999
    limit = 50
    skip = 0

    paginated = PaginationModel[int](data=int_list, total=total, limit=limit, skip=skip)

    assert paginated.total == total
    assert paginated.limit == limit
    assert paginated.skip == skip
    assert len(paginated.data) == 5
    for i in range(len(paginated.data)):
        assert paginated.data[i] == i+1


def test_pagination_model_invalid_data():
    str_list = []
    for i in range(1, 6):
        str_list.append(f'test{i}')

    total = -999
    limit = -50
    skip = -1
    with pytest.raises(pydantic.error_wrappers.ValidationError) as validation_error:
        PaginationModel[int](data=str_list, total=total, limit=limit, skip=skip)

    validation_errors = validation_error.value.errors()

    for i in range(0, 5):
        assert validation_errors[i]["loc"][0] == 'data'
        assert validation_errors[i]["loc"][1] == i
        assert validation_errors[i]["msg"] == "value is not a valid integer"
        assert validation_errors[i]["type"] == "type_error.integer"
    for i in range(5, 8):
        assert validation_errors[i]["msg"] == "ensure this value is greater than -1"
        assert validation_errors[i]["type"] == "value_error.number.not_gt"


def test_pagination_model_findings():
    findings = []
    for i in range(1, 6):
        finding = DBfinding(file_path=f"file_path_{i}",
                            line_number=i,
                            commit_id=f"commit_id_{i}",
                            commit_message=f"commit_message_{i}",
                            commit_timestamp=datetime.utcnow(),
                            author=f"author_{i}",
                            email=f"email_{i}",
                            status=FindingStatus.NOT_ANALYZED,
                            comment="",
                            rule_name=f"rule_{i}",
                            event_sent_on=datetime.utcnow(),
                            branch_info_id=1)
        finding.id_ = i
        findings.append(FindingRead.create_from_db_entities(finding, scan_ids=[]))

    total = 999
    limit = 50
    skip = 0

    paginated = PaginationModel[FindingRead](data=findings, total=total, limit=limit, skip=skip)

    assert paginated.total == total
    assert paginated.limit == limit
    assert paginated.skip == skip
    assert len(paginated.data) == 5
    for i in range(len(paginated.data)):
        assert paginated.data[i].id_ == i+1
