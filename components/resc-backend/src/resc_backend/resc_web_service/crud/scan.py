# pylint: disable=E1101
# Standard Library
from datetime import datetime
from typing import List

# Third Party
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.schema import scan as scan_schema
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.scan_type import ScanType


def get_scan(db_connection: Session, scan_id: int) -> model.DBscan:
    scan = db_connection.query(model.DBscan).filter(model.scan.DBscan.id_ == scan_id).first()
    return scan


def get_latest_scan_for_branch(db_connection: Session, branch_id: int) -> model.DBscan:
    """
        Retrieve the most recent scan of a given branch object
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch object for which to retrieve the most recent scan
    :return: scan
        scan object having the most recent timestamp for a given branch object
    """
    subquery = (db_connection.query(func.max(model.DBscan.timestamp).label("max_time"))
                .filter(model.scan.DBscan.branch_id == branch_id)).subquery()

    scan = db_connection.query(model.DBscan) \
        .join(subquery,
              and_(model.DBscan.timestamp == subquery.c.max_time)) \
        .filter(model.scan.DBscan.branch_id == branch_id).first()

    return scan


def get_scans(db_connection: Session, skip: int = 0,
              limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT, branch_id: int = -1) -> List[model.DBscan]:
    """
        Retrieve the scan records, ordered by scan_id and optionally filtered by branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        optional int filtering the branch for which to retrieve scans
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBscan]
        List of DBScan objects
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.DBscan)

    if branch_id > 0:
        query = query.filter(model.DBscan.branch_id == branch_id)

    scans = query.order_by(model.scan.DBscan.id_).offset(skip).limit(limit_val).all()
    return scans


def get_scans_count(db_connection: Session, branch_id: int = -1) -> int:
    """
        Retrieve count of scan records optionally filtered by VCS provider
    :param db_connection:
        Session of the database connection
    :param branch_id:
        optional int filtering the branch for which to retrieve scans
    :return: total_count
        count of scans
    """
    query = db_connection.query(func.count(model.DBscan.id_))

    if branch_id > 0:
        query = query.filter(model.DBscan.branch_id == branch_id)

    total_count = query.scalar()
    return total_count


def update_scan(db_connection: Session, scan_id: int, scan: scan_schema.ScanCreate) -> model.DBscan:
    db_scan = db_connection.query(model.DBscan).filter_by(id_=scan_id).first()
    db_scan.scan_type = scan.scan_type
    db_scan.last_scanned_commit = scan.last_scanned_commit
    db_scan.timestamp = scan.timestamp
    db_scan.increment_number = scan.increment_number
    db_scan.rule_pack = scan.rule_pack
    db_connection.commit()
    db_connection.refresh(db_scan)
    return db_scan


def create_scan(db_connection: Session, scan: scan_schema.ScanCreate) -> model.DBscan:
    db_scan = model.scan.DBscan(
        scan_type=scan.scan_type,
        last_scanned_commit=scan.last_scanned_commit,
        branch_id=scan.branch_id,
        timestamp=scan.timestamp,
        increment_number=scan.increment_number,
        rule_pack=scan.rule_pack
    )
    db_connection.add(db_scan)
    db_connection.commit()
    db_connection.refresh(db_scan)
    return db_scan


def delete_scan(db_connection: Session, scan_id: int):
    db_scan = db_connection.query(model.DBscan).filter_by(id_=scan_id).first()
    db_connection.delete(db_scan)
    db_connection.commit()
    return db_scan


def get_latest_scan_for_repository_for_master_branch(db_connection: Session, repository_id: int) -> model.DBscan:
    """
        Retrieve the most recent scan of a given repository object
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository object for which to retrieve the most recent scan
    :return: scan
        scan object having the most recent timestamp for a given repository object
    """
    master_branch = ['master', 'main']
    subquery = (db_connection.query(func.max(model.DBscan.timestamp).label("max_time"))
                .filter(model.scan.DBscan.branch_id == model.branch.DBbranch.id_)
                .filter(model.branch.DBbranch.repository_id == repository_id)
                .filter(func.lower(model.branch.DBbranch.branch_name).in_(master_branch))
                ).subquery()

    scan = db_connection.query(model.DBscan) \
        .join(subquery,
              and_(model.DBscan.timestamp == subquery.c.max_time)) \
        .first()

    return scan


def get_branch_findings_metadata_for_latest_scan(db_connection: Session, branch_id: int,
                                                 scan_timestamp: datetime):
    """
        Retrieves the finding metadata for latest scan of a branch from the database
    :param db_connection:
        Session of the database connection
    :param branch_id:
        branch id of the latest scan
    :param scan_timestamp:
        timestamp of the latest scan
    :return: findings_metadata
        findings_metadata containing the count for each status
    """
    scan_ids_latest_to_base = []
    scans = get_scans(db_connection=db_connection,
                      branch_id=branch_id, limit=1000000)
    scans.sort(key=lambda x: x.timestamp, reverse=True)
    for scan in scans:
        if scan.timestamp <= scan_timestamp:
            scan_ids_latest_to_base.append(scan.id_)
            if scan.scan_type == ScanType.BASE:
                break

    true_positive_count = false_positive_count = not_analyzed_count = \
        under_review_count = clarification_required_count = 0
    if len(scan_ids_latest_to_base) > 0:
        findings_count_by_status = finding_crud.get_findings_count_by_status(
            db_connection, scan_ids=scan_ids_latest_to_base, finding_statuses=FindingStatus)
        for finding in findings_count_by_status:
            finding_status = finding[0]
            count = finding[1]
            if finding_status == FindingStatus.TRUE_POSITIVE:
                true_positive_count = count
            if finding_status == FindingStatus.FALSE_POSITIVE:
                false_positive_count = count
            if finding_status == FindingStatus.NOT_ANALYZED:
                not_analyzed_count = count
            if finding_status == FindingStatus.UNDER_REVIEW:
                under_review_count = count
            if finding_status == FindingStatus.CLARIFICATION_REQUIRED:
                clarification_required_count = count

    total_findings_count = true_positive_count + false_positive_count + not_analyzed_count \
        + under_review_count + clarification_required_count

    findings_metadata = {
        "true_positive": true_positive_count,
        "false_positive": false_positive_count,
        "not_analyzed": not_analyzed_count,
        "under_review": under_review_count,
        "clarification_required": clarification_required_count,
        "total_findings_count": total_findings_count
    }

    return findings_metadata
