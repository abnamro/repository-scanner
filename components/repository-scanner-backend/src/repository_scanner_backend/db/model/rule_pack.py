# Third Party
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

# First Party
from repository_scanner_backend.db.model import Base
from repository_scanner_backend.db.model.rule_allow_list import DBruleAllowList


class DBrulePack(Base):
    __tablename__ = "rule_pack"
    version = Column("version", String(100), primary_key=True)
    global_allow_list = Column(Integer, ForeignKey(DBruleAllowList.id_), nullable=True)
    active = Column(Boolean, nullable=False, default=False)

    def __init__(self, version: str, global_allow_list: int = None, active: bool = False):
        self.version = version
        self.global_allow_list = global_allow_list
        self.active = active

    @staticmethod
    def create_from_metadata(version: str, global_allow_list: int, active: bool):
        db_rule_pack = DBrulePack(
            version=version,
            global_allow_list=global_allow_list,
            active=active,
        )
        return db_rule_pack
