# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.schema import branch_info as branchInfo_schema


def get_branches_info(db_connection: Session, skip: int = 0,
                      limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT):
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    branches_info = db_connection.query(model.DBbranchInfo).order_by(
            model.branch_info.DBbranchInfo.id_).offset(skip).limit(limit_val).all()
    return branches_info


def get_branches_info_for_repository(db_connection: Session, repository_info_id: int, skip: int = 0,
                                     limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> [model.DBbranchInfo]:
    """
        Retrieve all branch_info child objects of a repository_info object from the database
    :param db_connection:
        Session of the database connection
    :param repository_info_id:
        id of the parent repository_info object of which to retrieve branch_info objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBbranchInfo]
        The output will contain a list of DBbranchInfo type objects,
        or an empty list if no branch_info was found for the given repository_info_id
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    branches_info = db_connection.query(model.DBbranchInfo)\
        .filter(model.DBbranchInfo.repository_info_id == repository_info_id)\
        .order_by(model.branch_info.DBbranchInfo.id_).offset(skip).limit(limit_val).all()
    return branches_info


def get_branches_info_count(db_connection: Session) -> int:
    """
        Retrieve count of branches_info records
    :param db_connection:
        Session of the database connection
    :return: total_count
        count of branches
    """
    total_count = db_connection.query(func.count(model.DBbranchInfo.id_)).scalar()
    return total_count


def get_branches_info_count_for_repository(db_connection: Session, repository_info_id: int) -> int:
    """
        Retrieve count of finding records of a given scan
    :param db_connection:
        Session of the database connection
    :param repository_info_id:
        id of the repository_info_id object for which to retrieve the count of branches
    :return: total_count
        count of branches
    """
    total_count = db_connection.query(func.count(model.DBbranchInfo.id_))\
        .filter(model.DBbranchInfo.repository_info_id == repository_info_id)\
        .scalar()
    return total_count


def get_branch_info(db_connection: Session, branch_info_id: int):
    branch_info = db_connection.query(model.DBbranchInfo)\
        .filter(model.branch_info.DBbranchInfo.id_ == branch_info_id).first()
    return branch_info


def update_branch_info(db_connection: Session, branch_info_id: int, branch_info: branchInfo_schema.BranchInfoCreate):
    db_branch_info = db_connection.query(model.DBbranchInfo).filter_by(id_=branch_info_id).first()

    db_branch_info.branch_name = branch_info.branch_name
    db_branch_info.last_scanned_commit = branch_info.last_scanned_commit

    db_connection.commit()
    db_connection.refresh(db_branch_info)
    return db_branch_info


def create_branch_info(db_connection: Session, branch_info: branchInfo_schema.BranchInfoCreate):
    db_branch_info = model.branch_info.DBbranchInfo(
        repository_info_id=branch_info.repository_info_id,
        branch_id=branch_info.branch_id,
        branch_name=branch_info.branch_name,
        last_scanned_commit=branch_info.last_scanned_commit
    )
    db_connection.add(db_branch_info)
    db_connection.commit()
    db_connection.refresh(db_branch_info)
    return db_branch_info


def create_branch_info_if_not_exists(db_connection: Session, branch_info: branchInfo_schema.BranchInfoCreate):
    # Query the database to see if the branch_info object exists based on the unique constraint parameters
    db_select_branch_info = db_connection.query(model.DBbranchInfo) \
        .filter(model.DBbranchInfo.branch_id == branch_info.branch_id,
                model.DBbranchInfo.repository_info_id == branch_info.repository_info_id).first()
    if db_select_branch_info is not None:
        return db_select_branch_info

    # Create non-existing branch_info object
    return create_branch_info(db_connection, branch_info)


def delete_branch_info(db_connection: Session, branch_info_id: int):
    db_branch_info = db_connection.query(model.DBbranchInfo).filter_by(id_=branch_info_id).first()
    db_connection.delete(db_branch_info)
    db_connection.commit()
    return db_branch_info


def get_findings_metadata_by_branch_info_id(db_connection: Session, branch_info_id: int):
    """
        Retrieves the finding metadata for a branch id from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param branch_info_id:
        id of the branch for which findings metadata to be retrieved
    :return: findings_metadata
        findings_metadata containing the count for each status
    """

    latest_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_info_id=branch_info_id)

    if latest_scan is not None:
        findings_metadata = scan_crud.get_branch_findings_metadata_for_latest_scan(
                db_connection, branch_info_id=latest_scan.branch_info_id, scan_timestamp=latest_scan.timestamp)
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
