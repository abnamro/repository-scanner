# Standard Library
import sys
import unittest
from datetime import datetime

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from repository_scanner_backend.db.model import (
    Base,
    DBbranchInfo,
    DBfinding,
    DBrepositoryInfo,
    DBrule,
    DBscan,
    DBscanFinding,
    DBVcsInstance
)
from repository_scanner_backend.db.model.rule_pack import DBrulePack
from repository_scanner_backend.resc_web_service.schema.finding import FindingCreate
from repository_scanner_backend.resc_web_service.schema.finding_status import FindingStatus

sys.path.insert(0, "src")


class TestFinding(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)
        self.vcs_instance = DBVcsInstance(name="name",
                                          provider_type="provider_type",
                                          scheme="scheme",
                                          hostname="hostname",
                                          port=123,
                                          organization="organization",
                                          scope="scope",
                                          exceptions="exceptions")
        self.session.add(self.vcs_instance)

        self.repository_info = DBrepositoryInfo(project_key='TEST',
                                                repository_id=1,
                                                repository_name="test_temp",
                                                repository_url="fake.url.com",
                                                vcs_instance=1)
        self.session.add(self.repository_info)

        self.branch_info = DBbranchInfo(repository_info_id=1,
                                        branch_name="test_temp",
                                        branch_id='master',
                                        last_scanned_commit="FAKE_HASH")
        self.session.add(self.branch_info)

        self.rule_pack = DBrulePack(version="1.2")

        self.rule = DBrule(rule_pack="1.2", rule_name="fake rule", description="fake1, fake2, fake3")

        self.scan = DBscan(branch_info_id=1, scan_type="BASE",
                           last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(), rule_pack="1.2",
                           increment_number=1)

        self.session.add(self.scan)

        self.finding = DBfinding(file_path="/path/to/file/",
                                 line_number=1,
                                 commit_id="2",
                                 commit_message="Fake commit message",
                                 commit_timestamp=datetime.utcnow(),
                                 author="fake author",
                                 email="fake.author@fake-domain.com",
                                 status=FindingStatus.NOT_ANALYZED,
                                 comment="fake comment",
                                 rule_name="rule_1",
                                 event_sent_on=datetime.utcnow(),
                                 branch_info_id=1)
        self.scan_finding = DBscanFinding(finding_id=1, scan_id=1)
        self.session.add(self.finding)

        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.session.close()

    def test_query_all_finding(self):
        expected = [self.finding]
        result = self.session.query(DBfinding).all()
        self.assertEqual(result, expected)

    def test_create_from_finding(self):
        expected = self.finding
        finding = FindingCreate(file_path=self.finding.file_path,
                                line_number=self.finding.line_number,
                                commit_id=self.finding.commit_id,
                                commit_message=self.finding.commit_message,
                                commit_timestamp=self.finding.commit_timestamp,
                                author=self.finding.author,
                                email=self.finding.email,
                                status=self.finding.status,
                                comment=self.finding.comment,
                                rule_name=self.finding.rule_name,
                                event_sent_on=self.finding.event_sent_on,
                                scan_ids=[self.scan_finding.scan_id],
                                branch_info_id=self.finding.branch_info_id)
        result = DBfinding.create_from_finding(finding)
        self.assertEqual(result.file_path, expected.file_path)
        self.assertEqual(result.line_number, expected.line_number)
        self.assertEqual(result.commit_id, expected.commit_id)
        self.assertEqual(result.commit_message, expected.commit_message)
        self.assertEqual(result.commit_timestamp, expected.commit_timestamp)
