# Standard Library
import sys
import unittest

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from resc_backend.db.model import Base, DBrepository, DBVcsInstance

sys.path.insert(0, "src")


class TestRepository(unittest.TestCase):
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
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_all_repository(self):
        expected = [self.repository]
        result = self.session.query(DBrepository).all()
        self.assertEqual(result, expected)
