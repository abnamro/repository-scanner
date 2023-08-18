# Standard Library
from datetime import datetime

# Third Party
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

# First Party
from resc_backend.db.model import Base
from resc_backend.db.model.rule_allow_list import DBruleAllowList


class DBrulePack(Base):
    __tablename__ = "rule_pack"
    version = Column("version", String(100), primary_key=True)
    global_allow_list = Column(Integer, ForeignKey(DBruleAllowList.id_), nullable=True)
    active = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, version: str, global_allow_list: int = None, active: bool = False,
                 created: datetime = datetime.utcnow()):
        self.version = version
        self.global_allow_list = global_allow_list
        self.active = active
        self.created = created

    @staticmethod
    def create_from_metadata(version: str, global_allow_list: int, active: bool, created: datetime):
        db_rule_pack = DBrulePack(
            version=version,
            global_allow_list=global_allow_list,
            active=active,
            created=created
        )
        return db_rule_pack
