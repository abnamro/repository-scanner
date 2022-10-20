# Third Party
from sqlalchemy import Column, Integer, String, Text

# First Party
from resc_backend.db.model import Base


class DBruleAllowList(Base):
    __tablename__ = "rule_allow_list"
    id_ = Column("id", Integer, primary_key=True)
    description = Column(String(2000), nullable=True)
    regexes = Column(Text, nullable=True)
    paths = Column(Text, nullable=True)
    commits = Column(Text, nullable=True)
    stop_words = Column(Text, nullable=True)

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
