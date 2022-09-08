# Standard Library
import sys
import unittest
from datetime import datetime

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from repository_scanner_backend.db.model import Base, DBbranchInfo, DBrepositoryInfo, DBscan, DBVcsInstance
from repository_scanner_backend.db.model.rule_pack import DBrulePack

sys.path.insert(0, "src")


class TestScan(unittest.TestCase):
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

        self.scan = DBscan(branch_info_id=1, scan_type="BASE",
                           last_scanned_commit="FAKE_HASH", timestamp=datetime.utcnow(), rule_pack="1.2",
                           increment_number=1)

        self.session.add(self.scan)

        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_all_scan(self):
        expected = [self.scan]
        result = self.session.query(DBscan).all()
        self.assertEqual(result, expected)
