# Standard Library
import sys
import unittest
from datetime import datetime

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from resc_backend.db.model import Base, DBfinding, DBrepository, DBrule, DBscan, DBscanFinding, DBVcsInstance
from resc_backend.db.model.rule_pack import DBrulePack
from resc_backend.resc_web_service.schema.finding import FindingCreate

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

        self.repository = DBrepository(project_key='TEST',
                                       repository_id=1,
                                       repository_name="test_temp",
                                       repository_url="fake.url.com",
                                       vcs_instance=1)
        self.session.add(self.repository)

        self.rule_pack = DBrulePack(version="1.2")

        self.rule = DBrule(rule_pack="1.2", rule_name="fake rule", description="fake1, fake2, fake3")

        self.scan = DBscan(repository_id=1, scan_type="BASE",
                           last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(), rule_pack="1.2",
                           increment_number=1)

        self.session.add(self.scan)

        self.finding = DBfinding(file_path="/path/to/file/",
                                 line_number=1,
                                 column_start=1,
                                 column_end=10,
                                 commit_id="2",
                                 commit_message="Fake commit message",
                                 commit_timestamp=datetime.utcnow(),
                                 author="fake author",
                                 email="fake.author@fake-domain.com",
                                 rule_name="rule_1",
                                 event_sent_on=datetime.utcnow(),
                                 repository_id=1)
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
                                column_start=self.finding.column_start,
                                column_end=self.finding.column_end,
                                commit_id=self.finding.commit_id,
                                commit_message=self.finding.commit_message,
                                commit_timestamp=self.finding.commit_timestamp,
                                author=self.finding.author,
                                email=self.finding.email,
                                rule_name=self.finding.rule_name,
                                event_sent_on=self.finding.event_sent_on,
                                scan_ids=[self.scan_finding.scan_id],
                                repository_id=self.finding.repository_id)
        result = DBfinding.create_from_finding(finding)
        self.assertEqual(result.file_path, expected.file_path)
        self.assertEqual(result.line_number, expected.line_number)
        self.assertEqual(result.column_start, expected.column_start)
        self.assertEqual(result.column_end, expected.column_end)
        self.assertEqual(result.commit_id, expected.commit_id)
        self.assertEqual(result.commit_message, expected.commit_message)
        self.assertEqual(result.commit_timestamp, expected.commit_timestamp)
