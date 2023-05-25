# Third Party
from sqlalchemy import Column, ForeignKey, Integer

# First Party
from resc_backend.db.model import Base


class DBruleTag(Base):
    __tablename__ = "rule_tag"
    rule_id = Column(Integer, ForeignKey("rules.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)

    def __init__(self, rule_id: int, tag_id: int):

        self.rule_id = rule_id
        self.tag_id = tag_id
