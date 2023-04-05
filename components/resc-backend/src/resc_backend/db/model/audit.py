# Standard Library
import html
from datetime import datetime

# Third Party
from sqlalchemy import Column, DateTime, Enum, Integer, String

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class DBaudit(Base):
    __tablename__ = "audit"
    id_ = Column("id", Integer, primary_key=True)
    status = Column(Enum(FindingStatus), default=FindingStatus.NOT_ANALYZED, server_default="NOT_ANALYZED",
                    nullable=False)
    author = Column(String(200))
    comment = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, status, author, comment, timestamp):
        self.status = status
        self.author = author
        self.comment = comment
        self.timestamp = timestamp

    @staticmethod
    def create_from_metadata(status: str, author: str, comment: str, timestamp: datetime):
        sanitized_comment = html.escape(comment) if comment else comment
        db_audit = DBaudit(
            author=author,
            status=status,
            comment=sanitized_comment,
            timestamp=timestamp
        )
        return db_audit
