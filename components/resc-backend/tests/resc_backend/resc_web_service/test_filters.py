# Standard Library
from datetime import datetime

# Third Party
import pytest

# First Party
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


def test_findings_filter_basic_vcs_provider():
    findings_filter = FindingsFilter(vcs_providers=[VCSProviders.BITBUCKET])
    assert findings_filter.vcs_providers == [VCSProviders.BITBUCKET]


def test_findings_filter_multiple_values():
    params = {"vcs_providers": [VCSProviders.AZURE_DEVOPS, VCSProviders.BITBUCKET],
              "finding_statuses": [FindingStatus.NOT_ANALYZED]}
    findings_filter = FindingsFilter(**params)
    assert findings_filter.vcs_providers == [VCSProviders.AZURE_DEVOPS, VCSProviders.BITBUCKET]
    assert findings_filter.finding_statuses == [FindingStatus.NOT_ANALYZED]


def test_findings_filter_valid_date_range():

    findings_filter = FindingsFilter(
        start_date_time=datetime.strptime("1970-11-11T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        end_date_time=datetime.strptime("1970-11-11T00:00:01", "%Y-%m-%dT%H:%M:%S")
    )
    assert findings_filter


def test_findings_filter_invalid_date_range():
    with pytest.raises(ValueError) as value_error:
        FindingsFilter(
            start_date_time=datetime.strptime("1970-11-11T00:00:01", "%Y-%m-%dT%H:%M:%S"),
            end_date_time=datetime.strptime("1970-11-11T00:00:00", "%Y-%m-%dT%H:%M:%S")
        )

        assert "the start of the date range needs to be prior to the end of it." in str(value_error.value)
