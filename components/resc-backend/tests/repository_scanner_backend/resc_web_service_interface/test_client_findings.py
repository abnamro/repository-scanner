# Standard Library
import json
from datetime import datetime
from unittest.mock import patch

# First Party
from resc_backend.resc_web_service.schema.finding import FindingCreate
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service_interface.findings import create_findings

findings = []
for i in range(1, 6):
    findings.append(FindingCreate(scan_ids=[i],
                                  file_path=f"file_path_{i}",
                                  line_number=i,
                                  commit_id=f"commit_id_{i}",
                                  commit_message=f"commit_message_{i}",
                                  commit_timestamp=datetime.utcnow(),
                                  author=f"author_{i}",
                                  email=f"email_{i}",
                                  status=FindingStatus.NOT_ANALYZED,
                                  comment=f"comment_{i}",
                                  rule_name=f"rule_{i}",
                                  branch_info_id=1)
                    )


@patch("requests.post")
def test_create_findings(post):
    expected_url = 'https://fake-host.com/resc/v1/findings'
    url = 'https://fake-host.com'

    findings_json = []
    for finding in findings:
        findings_json.append(json.loads(finding.json()))

    _ = create_findings(url, findings)
    post.assert_called_once()
    post.assert_called_with(expected_url, json=findings_json, proxies={'http': '', 'https': ''})
