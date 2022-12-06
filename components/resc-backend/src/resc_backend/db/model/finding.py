# pylint: disable=R0902
# Standard Library
from datetime import datetime

# Third Party
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class DBfinding(Base):
    __tablename__ = "finding"
    id_ = Column("id", Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branch.id"), nullable=False)
    rule_name = Column(String(400), nullable=False)
    file_path = Column(String(500), nullable=False)
    line_number = Column(Integer, nullable=False)
    commit_id = Column(String(120))
    commit_message = Column(Text)
    commit_timestamp = Column(DateTime, default=datetime.utcnow().isoformat())
    author = Column(String(200))
    email = Column(String(100))
    status = Column(Enum(FindingStatus), default=FindingStatus.NOT_ANALYZED, server_default="NOT_ANALYZED",
                    nullable=False)
    comment = Column(String(255), nullable=True)
    event_sent_on = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("commit_id", "branch_id", "rule_name", "file_path", "line_number",
                                       name="uc_finding_per_branch"),)

    def __init__(self, rule_name, file_path, line_number, commit_id, commit_message, commit_timestamp, author,
                 email, status, comment, event_sent_on, branch_id):
        self.email = email
        self.author = author
        self.commit_timestamp = commit_timestamp
        self.commit_message = commit_message
        self.commit_id = commit_id
        self.line_number = line_number
        self.file_path = file_path
        self.rule_name = rule_name
        self.status = status
        self.comment = comment
        self.event_sent_on = event_sent_on
        self.branch_id = branch_id

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
            status=finding.status,
            comment=finding.comment,
            event_sent_on=finding.event_sent_on,
            branch_id=finding.branch_id
        )
        return db_finding
