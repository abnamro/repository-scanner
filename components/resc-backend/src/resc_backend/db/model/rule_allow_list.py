# Third Party
from sqlalchemy import Column, Integer, String

# First Party
from resc_backend.db.model import Base


class DBruleAllowList(Base):
    __tablename__ = "rule_allow_list"
    id_ = Column("id", Integer, primary_key=True)
    description = Column(String(400), nullable=False)
    regexes = Column(String(400), nullable=True)
    paths = Column(String(400), nullable=True)
    commits = Column(String(400), nullable=True)
    stop_words = Column(String(400), nullable=True)

    def __init__(self, description: str, regexes: str = None, paths: str = None, commits: str = None,
                 stop_words: str = None):
        self.description = description
        self.regexes = regexes
        self.paths = paths
        self.commits = commits
        self.stop_words = stop_words

    @staticmethod
    def create_from_metadata(description: str, regexes: str, paths: str, commits: str, stop_words: str):
        db_rule_allow_list = DBruleAllowList(
            description=description,
            regexes=regexes,
            paths=paths,
            commits=commits,
            stop_words=stop_words
        )
        return db_rule_allow_list
