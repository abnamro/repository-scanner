# Standard Library
import unittest
from datetime import datetime

# First Party
from resc_backend.resc_web_service.schema.detailed_finding import DetailedFindingRead
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class TestDetailedFindings(unittest.TestCase):
    def setUp(self):
        self.detailed_findings_ado = []
        self.detailed_findings_bitbucket = []
        for i in range(1, 6):
            self.detailed_findings_ado.append(DetailedFindingRead(
                id_=i,
                file_path=f"file_path_{i}",
                line_number=i,
                column_start=i,
                column_end=i,
                commit_id=f"commit_id_{i}",
                commit_message=f"commit_message_{i}",
                commit_timestamp=datetime.utcnow(),
                author=f"author_{i}",
                email=f"email_{i}",
                status=FindingStatus.NOT_ANALYZED,
                comment=f"comment_{i}",
                rule_name=f"rule_name_{i}",
                rule_pack=f"rule_pack_{i}",
                project_key=f"project_key_{i}",
                repository_name=f"repository_name_{i}",
                repository_url=f"http://fake.repo.com/{i}",
                timestamp=datetime.utcnow(),
                vcs_provider="AZURE_DEVOPS",
                last_scanned_commit=f"last_scanned_commit_{i}",
                commit_url=f"commit_url_{i}",
                scan_id=i),
            )

        for index in range(1, 6):
            self.detailed_findings_bitbucket.append(DetailedFindingRead(
                id_=index,
                file_path=f"file_path_{index}",
                line_number=index,
                column_start=index,
                column_end=index,
                commit_id=f"commit_id_{index}",
                commit_message=f"commit_message_{index}",
                commit_timestamp=datetime.utcnow(),
                author=f"author_{index}",
                email=f"email_{index}",
                status=FindingStatus.NOT_ANALYZED,
                comment=f"comment_{index}",
                rule_name=f"rule_name_{index}",
                rule_pack=f"rule_pack_{index}",
                project_key=f"project_key_{index}",
                repository_name=f"repository_name_{index}",
                repository_url=f"https://dummy-bitbucket-instance.com/projects/project_key_{index}",
                timestamp=datetime.utcnow(),
                vcs_provider="BITBUCKET",
                last_scanned_commit=f"last_scanned_commit_{index}",
                commit_url=f"commit_url_{index}",
                scan_id=index),
            )

    def test_get_commit_url_by_vcs_provider_ado(self):
        detailed_findings = self.detailed_findings_ado
        for index, finding in enumerate(detailed_findings):
            assert detailed_findings[
                       index].commit_url == f"http://fake.repo.com/{index + 1}/commit/commit_id_{index + 1}" \
                                            f"?path=/file_path_{index + 1}"

    def test_get_commit_url_by_vcs_provider_bitbucket(self):
        detailed_findings = self.detailed_findings_bitbucket
        for idx, finding in enumerate(detailed_findings):
            assert detailed_findings[idx].commit_url == f"https://dummy-bitbucket-instance.com" \
                                                        f"/projects/project_key_{idx + 1}" \
                                                        f"/repos/repository_name_{idx + 1}" \
                                                        f"/browse/file_path_{idx + 1}?at=commit_id_{idx + 1}"
