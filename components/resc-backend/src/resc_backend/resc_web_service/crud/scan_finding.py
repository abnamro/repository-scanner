# Standard Library
from typing import List

# First Party
from resc_backend.db import model
from resc_backend.db.connection import Session
from resc_backend.db.model import DBscanFinding


def create_scan_findings(db_connection: Session, scan_findings: List[DBscanFinding]) -> int:
    if len(scan_findings) < 1:
        # Function is called with an empty list of findings
        return 0

    # load existing scan findings for this scan into the session
    scan_id = scan_findings[0].scan_id
    _ = db_connection.query(model.DBscanFinding).filter(DBscanFinding.scan_id == scan_id).all()

    # merge the new scan findings into the session, ignoring duplicates
    for scan_finding in scan_findings:
        db_connection.merge(scan_finding)

    db_connection.commit()

    return len(scan_findings)


def get_scan_findings(db_connection: Session, finding_id: int) -> List[DBscanFinding]:
    scan_findings = db_connection.query(model.DBscanFinding)
    scan_findings = scan_findings.filter(model.scan_finding.DBscanFinding.finding_id == finding_id).all()
    return scan_findings
