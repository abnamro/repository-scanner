# Standard Library
import sys
import unittest

# Third Party
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# First Party
from resc_backend.db.model import Base, DBrule
from resc_backend.db.model.rule_pack import DBrulePack

sys.path.insert(0, "src")


class TestRule(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)

        self.rule_pack = DBrulePack(version="1.2")

        self.rule = DBrule(rule_pack="1.2", rule_name="fake_rule", description="fake1, fake2, fake3", regex=".*")

        self.session.add(self.rule)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_all_repository(self):
        expected = [self.rule]
        result = self.session.query(DBrule).all()
        self.assertEqual(result, expected)
