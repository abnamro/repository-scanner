# Third Party
from sqlalchemy import Column, ForeignKey, Integer

# First Party
from resc_backend.db.model import Base


class DBfindingAudit(Base):
    __tablename__ = "finding_audit"
    finding_id = Column(Integer, ForeignKey("finding.id"), primary_key=True)
    audit_id = Column(Integer, ForeignKey("audit.id"), primary_key=True)

    def __init__(self, finding_id: int, audit_id: int):

        self.finding_id = finding_id
        self.audit_id = audit_id
