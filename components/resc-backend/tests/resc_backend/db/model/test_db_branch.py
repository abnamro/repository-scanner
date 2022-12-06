# Standard Library
import sys
import unittest

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from resc_backend.db.model import Base, DBbranch, DBrepository, DBVcsInstance

sys.path.insert(0, "src")


class TestBranch(unittest.TestCase):
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

        self.branch = DBbranch(repository_id=1,
                               branch_name="test_temp",
                               branch_id='master',
                               latest_commit="FAKE_HASH")
        self.session.add(self.branch)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_all_branch(self):
        expected = [self.branch]
        result = self.session.query(DBbranch).all()
        self.assertEqual(result, expected)
