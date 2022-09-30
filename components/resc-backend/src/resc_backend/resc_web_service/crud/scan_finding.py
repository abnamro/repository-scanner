# Standard Library
from typing import List

# Third Party
from sqlalchemy.exc import IntegrityError

# First Party
from resc_backend.db import model
from resc_backend.db.connection import Session
from resc_backend.db.model import DBscanFinding


def create_scan_findings(db_connection: Session, scan_findings: List[DBscanFinding]) -> int:

    if len(scan_findings) < 1:
        # Function is called with an empty list of findings
        return 0
    for scan_finding in scan_findings:

        try:
            with db_connection.begin_nested():
                db_connection.merge(scan_finding)
                db_connection.flush()
            db_connection.commit()
        except IntegrityError as integrity_error:

            if "uc_scan_finding" not in str(integrity_error):
                raise integrity_error

    return len(scan_findings)


def create_scan_finding(db_connection: Session, scan_finding: DBscanFinding) -> DBscanFinding:

    db_connection.add_all(scan_finding)
    db_connection.commit()
    return scan_finding


def delete_scan_finding(db_connection: Session, finding_id: int) -> List[DBscanFinding]:
    db_scan_findings = db_connection.query(model.DBscanFinding).filter_by(finding_id=finding_id).all()
    for db_scan_finding in db_scan_findings:
        db_connection.delete(db_scan_finding)
    db_connection.commit()
    return db_scan_findings


def get_scan_findings(db_connection: Session, finding_id: int) -> List[DBscanFinding]:
    scan_findings = db_connection.query(model.DBscanFinding)
    scan_findings = scan_findings.filter(model.scan_finding.DBscanFinding.finding_id == finding_id).all()
    return scan_findings
