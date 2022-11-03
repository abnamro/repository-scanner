# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.schema import branch as branch_schema


def get_branches(db_connection: Session, skip: int = 0,
                 limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT):
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    branches = db_connection.query(model.DBbranch).order_by(
        model.branch.DBbranch.id_).offset(skip).limit(limit_val).all()
    return branches


def get_branches_for_repository(db_connection: Session, repository_id: int, skip: int = 0,
                                limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> [model.DBbranch]:
    """
        Retrieve all branch child objects of a repository object from the database
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the parent repository object of which to retrieve branch objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBbranch]
        The output will contain a list of DBbranch type objects,
        or an empty list if no branch was found for the given repository_id
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    branches = db_connection.query(model.DBbranch) \
        .filter(model.DBbranch.repository_id == repository_id) \
        .order_by(model.branch.DBbranch.id_).offset(skip).limit(limit_val).all()
    return branches


def get_branches_count(db_connection: Session) -> int:
    """
        Retrieve count of branches records
    :param db_connection:
        Session of the database connection
    :return: total_count
        count of branches
    """
    total_count = db_connection.query(func.count(model.DBbranch.id_)).scalar()
    return total_count


def get_branches_count_for_repository(db_connection: Session, repository_id: int) -> int:
    """
        Retrieve count of finding records of a given scan
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository_id object for which to retrieve the count of branches
    :return: total_count
        count of branches
    """
    total_count = db_connection.query(func.count(model.DBbranch.id_)) \
        .filter(model.DBbranch.repository_id == repository_id) \
        .scalar()
    return total_count


def get_branch(db_connection: Session, branch_id: int):
    branch = db_connection.query(model.DBbranch) \
        .filter(model.branch.DBbranch.id_ == branch_id).first()
    return branch


def update_branch(db_connection: Session, branch_id: int, branch: branch_schema.BranchCreate):
    db_branch = db_connection.query(model.DBbranch).filter_by(id_=branch_id).first()

    db_branch.branch_name = branch.branch_name
    db_branch.last_scanned_commit = branch.last_scanned_commit

    db_connection.commit()
    db_connection.refresh(db_branch)
    return db_branch


def create_branch(db_connection: Session, branch: branch_schema.BranchCreate):
    db_branch = model.branch.DBbranch(
        repository_id=branch.repository_id,
        branch_id=branch.branch_id,
        branch_name=branch.branch_name,
        last_scanned_commit=branch.last_scanned_commit
    )
    db_connection.add(db_branch)
    db_connection.commit()
    db_connection.refresh(db_branch)
    return db_branch


def create_branch_if_not_exists(db_connection: Session, branch: branch_schema.BranchCreate):
    # Query the database to see if the branch object exists based on the unique constraint parameters
    db_select_branch = db_connection.query(model.DBbranch) \
        .filter(model.DBbranch.branch_id == branch.branch_id,
                model.DBbranch.repository_id == branch.repository_id).first()
    if db_select_branch is not None:
        return db_select_branch

    # Create non-existing branch object
    return create_branch(db_connection, branch)


def get_findings_metadata_by_branch_id(db_connection: Session, branch_id: int):
    """
        Retrieves the finding metadata for a branch id from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch for which findings metadata to be retrieved
    :return: findings_metadata
        findings_metadata containing the count for each status
    """

    latest_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_id=branch_id)

    if latest_scan is not None:
        findings_metadata = scan_crud.get_branch_findings_metadata_for_latest_scan(
            db_connection, branch_id=latest_scan.branch_id, scan_timestamp=latest_scan.timestamp)
    else:
        findings_metadata = {
            "true_positive": 0,
            "false_positive": 0,
            "not_analyzed": 0,
            "under_review": 0,
            "clarification_required": 0,
            "total_findings_count": 0
        }

    return findings_metadata


def delete_branch(db_connection: Session, branch_id: int):
    """
        Delete a branch object
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch to be deleted
    """
    if branch_id:
        db_connection.query(model.DBbranch) \
            .filter(model.branch.DBbranch.id_ == branch_id) \
            .delete(synchronize_session=False)
        db_connection.commit()


def delete_scans_by_branch_id(db_connection: Session, branch_id: int):
    """
        Delete scans for a given branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch
    """
    if branch_id:
        db_connection.query(model.DBscan) \
            .filter(model.scan.DBscan.branch_id == branch_id) \
            .delete(synchronize_session=False)
        db_connection.commit()


def delete_scan_finding_by_branch_id(db_connection: Session, branch_id: int):
    """
        Delete scan findings for a given branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch
    """
    if branch_id:
        db_connection.query(model.DBscanFinding) \
            .filter(model.scan_finding.DBscanFinding.scan_id == model.scan.DBscan.id_,
                    model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_,
                    model.scan.DBscan.branch_id == model.finding.DBfinding.branch_id,
                    model.scan.DBscan.branch_id == branch_id) \
            .delete(synchronize_session=False)
        db_connection.commit()


def delete_findings_by_branch_id(db_connection: Session, branch_id: int):
    """
        Delete findings for a given branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch
    """
    if branch_id:
        db_connection.query(model.DBfinding) \
            .filter(model.finding.DBfinding.branch_id == branch_id) \
            .delete(synchronize_session=False)
        db_connection.commit()