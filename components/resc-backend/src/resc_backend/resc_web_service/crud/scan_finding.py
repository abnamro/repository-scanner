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


def delete_scan_finding(db_connection: Session, finding_id: int = None, scan_id: int = None):
    """
        Delete scan findings when finding id or scan id provided
    :param db_connection:
        Session of the database connection
    :param finding_id:
        optional, id of the finding
    :param scan_id:
        optional, id of the scan
    """
    if finding_id or scan_id:
        query = db_connection.query(model.DBscanFinding)
        if finding_id:
            query = query.filter(model.scan_finding.DBscanFinding.finding_id == finding_id)
        if scan_id:
            query = query.filter(model.scan_finding.DBscanFinding.scan_id == scan_id)
        query.delete(synchronize_session=False)
        db_connection.commit()


def delete_scan_finding_by_branch_id(db_connection: Session, branch_id: int):
    """
        Delete scan findings for a given branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch
    """
    db_connection.query(model.DBscanFinding) \
        .filter(model.scan_finding.DBscanFinding.scan_id == model.scan.DBscan.id_,
                model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_,
                model.scan.DBscan.branch_id == model.finding.DBfinding.branch_id,
                model.scan.DBscan.branch_id == branch_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_scan_finding_by_repository_id(db_connection: Session, repository_id: int):
    """
        Delete scan findings for a given repository
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository
    """
    db_connection.query(model.DBscanFinding) \
        .filter(model.scan_finding.DBscanFinding.scan_id == model.scan.DBscan.id_,
                model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_,
                model.scan.DBscan.branch_id == model.branch.DBbranch.id_,
                model.branch.DBbranch.repository_id == model.repository.DBrepository.id_,
                model.repository.DBrepository.id_ == repository_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_scan_finding_by_vcs_instance_id(db_connection: Session, vcs_instance_id: int):
    """
        Delete scan findings for a given vcs instance
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the vcs instance
    """
    db_connection.query(model.DBscanFinding) \
        .filter(model.scan_finding.DBscanFinding.scan_id == model.scan.DBscan.id_,
                model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_,
                model.scan.DBscan.branch_id == model.branch.DBbranch.id_,
                model.branch.DBbranch.repository_id == model.repository.DBrepository.id_,
                model.repository.DBrepository.vcs_instance == model.vcs_instance.DBVcsInstance.id_,
                model.vcs_instance.DBVcsInstance.id_ == vcs_instance_id) \
        .delete(synchronize_session=False)
    db_connection.commit()
