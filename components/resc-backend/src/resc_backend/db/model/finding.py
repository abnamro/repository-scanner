# pylint: disable=R0902
# Standard Library
from datetime import datetime

# Third Party
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

# First Party
from resc_backend.db.model import Base


class DBfinding(Base):
    __tablename__ = "finding"
    id_ = Column("id", Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=False)
    rule_name = Column(String(400), nullable=False)
    file_path = Column(String(500), nullable=False)
    line_number = Column(Integer, nullable=False)
    column_start = Column(Integer, nullable=False, default=0)
    column_end = Column(Integer, nullable=False, default=0)
    commit_id = Column(String(120))
    commit_message = Column(Text)
    commit_timestamp = Column(DateTime, default=datetime.utcnow().isoformat())
    author = Column(String(200))
    email = Column(String(100))
    event_sent_on = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("commit_id", "repository_id", "rule_name", "file_path", "line_number",
                                       "column_start", "column_end", name="uc_finding_per_repository"),)

    def __init__(self, rule_name, file_path, line_number, commit_id, commit_message, commit_timestamp, author,
                 email, event_sent_on, repository_id, column_start, column_end):
        self.email = email
        self.author = author
        self.commit_timestamp = commit_timestamp
        self.commit_message = commit_message
        self.commit_id = commit_id
        self.line_number = line_number
        self.file_path = file_path
        self.rule_name = rule_name
        self.event_sent_on = event_sent_on
        self.repository_id = repository_id
        self.column_start = column_start
        self.column_end = column_end

    @staticmethod
    def create_from_finding(finding):
        db_finding = DBfinding(
            rule_name=finding.rule_name,
            file_path=finding.file_path,
            line_number=finding.line_number,
            email=finding.email,
            commit_id=finding.commit_id,
            commit_message=finding.commit_message,
            commit_timestamp=finding.commit_timestamp,
            author=finding.author,
            event_sent_on=finding.event_sent_on,
            repository_id=finding.repository_id,
            column_start=finding.column_start,
            column_end=finding.column_end
        )
        return db_finding
