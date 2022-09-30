# Third Party
from sqlalchemy import Column, ForeignKey, Integer

# First Party
from resc_backend.db.model import Base


class DBscanFinding(Base):
    __tablename__ = "scan_finding"
    finding_id = Column(Integer, ForeignKey("finding.id"), primary_key=True)
    scan_id = Column(Integer, ForeignKey("scan.id"), primary_key=True)

    def __init__(self, finding_id: int, scan_id: int):

        self.finding_id = finding_id
        self.scan_id = scan_id
