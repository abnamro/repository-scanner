# pylint: disable=R0902
# Third Party
from sqlalchemy import Column, Integer, String, UniqueConstraint

# First Party
from resc_backend.db.model import Base


class DBtag(Base):
    __tablename__ = "tag"
    id_ = Column("id", Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    __table_args__ = (UniqueConstraint("name", name="unique_tag"),)

    def __init__(self, name: str):
        self.name = name
