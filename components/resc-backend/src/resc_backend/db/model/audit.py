# Standard Library
import html
from datetime import datetime

# Third Party
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class DBaudit(Base):
    __tablename__ = "audit"
    id_ = Column("id", Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("finding.id"), nullable=False)
    status = Column(Enum(FindingStatus), default=FindingStatus.NOT_ANALYZED, server_default="NOT_ANALYZED",
                    nullable=False)
    auditor = Column(String(200))
    comment = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, finding_id, status, auditor, comment, timestamp):
        sanitized_comment = html.escape(comment) if comment else comment
        self.finding_id = finding_id
        self.status = status
        self.auditor = auditor
        self.comment = sanitized_comment
        self.timestamp = timestamp

    @staticmethod
    def create_from_metadata(finding_id: int, status: str, auditor: str, comment: str, timestamp: datetime):
        sanitized_comment = html.escape(comment) if comment else comment
        db_audit = DBaudit(
            finding_id=finding_id,
            auditor=auditor,
            status=status,
            comment=sanitized_comment,
            timestamp=timestamp
        )
        return db_audit
