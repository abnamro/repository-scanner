# pylint: disable=R0902
# Third Party
from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint

# First Party
from repository_scanner_backend.db.model import Base
from repository_scanner_backend.db.model.rule_allow_list import DBruleAllowList
from repository_scanner_backend.db.model.rule_pack import DBrulePack


class DBrule(Base):
    __tablename__ = "rules"
    id_ = Column("id", Integer, primary_key=True)
    rule_pack = Column(String(100), ForeignKey(DBrulePack.version), nullable=False)
    allow_list = Column(Integer, ForeignKey(DBruleAllowList.id_), nullable=True)
    rule_name = Column(String(400), nullable=False)
    description = Column(String(400), nullable=False)
    tags = Column(String(400), nullable=True)
    entropy = Column(Float, nullable=True)
    secret_group = Column(Integer, nullable=True)
    regex = Column(String(1000), nullable=True)
    path = Column(String(1000), nullable=True)
    keywords = Column(String(400), nullable=True)
    __table_args__ = (UniqueConstraint("rule_name", "rule_pack", name="unique_rule_name_per_rule_pack_version"),)

    def __init__(self, rule_pack: str, rule_name: str, description: str, allow_list: int = None,
                 entropy: float = None, secret_group: str = None, regex: str = None, path: str = None, tags: str = None,
                 keywords: str = None):
        self.rule_pack = rule_pack
        self.allow_list = allow_list
        self.rule_name = rule_name
        self.description = description
        self.entropy = entropy
        self.secret_group = secret_group
        self.regex = regex
        self.path = path
        self.tags = tags
        self.keywords = keywords

    @staticmethod
    def create_from_metadata(rule_pack: str, rule_name: str, description: str, tags: str, entropy: float,
                             secret_group: str, regex: str, path: str, keywords: str,
                             allow_list: int):
        db_rule = DBrule(
            rule_pack=rule_pack,
            rule_name=rule_name,
            description=description,
            tags=tags,
            entropy=entropy,
            secret_group=secret_group,
            regex=regex,
            path=path,
            keywords=keywords,
            allow_list=allow_list
        )
        return db_rule
