# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import branch as branch_crud
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.crud import scan_finding as scan_finding_crud
from resc_backend.resc_web_service.schema import repository as repository_schema
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


def get_repositories(db_connection: Session, vcs_providers: [VCSProviders] = None, skip: int = 0,
                     limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT, project_filter: str = "",
                     repository_filter: str = ""):
    """
        Retrieve repository records optionally filtered
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param vcs_providers:
        optional [string] filtering the VCS provider
    :param project_filter:
        optional, filter on project name. Is used as a string contains filter
    :param repository_filter:
        optional, filter on repository name. Is used as a string contains filter
    :return: repositories
        list of DBrepository objects
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(
        model.DBrepository.id_,
        model.DBrepository.project_key,
        model.DBrepository.repository_id,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
        model.DBrepository.vcs_instance,
        model.DBVcsInstance.provider_type) \
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)

    if vcs_providers and vcs_providers is not None:
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_filter:
        query = query.filter(model.DBrepository.project_key == project_filter)

    if repository_filter:
        query = query.filter(model.DBrepository.repository_name == repository_filter)

    repositories = query.order_by(model.DBrepository.id_).offset(skip).limit(limit_val).all()
    return repositories


def get_repositories_count(db_connection: Session, vcs_providers: [VCSProviders] = None, project_filter: str = "",
                           repository_filter: str = "") -> int:
    """
        Retrieve count of repository records optionally filtered
    :param db_connection:
        Session of the database connection
    :param vcs_providers:
        optional [string] filtering the VCS provider
    :param project_filter:
        optional, filter on project name
    :param repository_filter:
        optional, filter on repository name
    :return: total_count
        count of repositories
    """
    query = db_connection.query(func.count(model.DBrepository.id_))

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_filter:
        query = query.filter(model.DBrepository.project_key == project_filter)

    if repository_filter:
        query = query.filter(model.DBrepository.repository_name == repository_filter)

    total_count = query.scalar()
    return total_count


def get_repository(db_connection: Session, repository_id: int):
    repository = db_connection.query(model.DBrepository) \
        .filter(model.repository.DBrepository.id_ == repository_id).first()
    return repository


def update_repository(
        db_connection: Session, repository_id: int, repository: repository_schema.RepositoryCreate):
    db_repository = db_connection.query(model.DBrepository).filter_by(id_=repository_id).first()

    db_repository.repository_name = repository.repository_name
    db_repository.repository_url = repository.repository_url
    db_repository.vcs_instance = repository.vcs_instance

    db_connection.commit()
    db_connection.refresh(db_repository)
    return db_repository


def create_repository(db_connection: Session, repository: repository_schema.RepositoryCreate):
    db_repository = model.repository.DBrepository(
        project_key=repository.project_key,
        repository_id=repository.repository_id,
        repository_name=repository.repository_name,
        repository_url=repository.repository_url,
        vcs_instance=repository.vcs_instance
    )
    db_connection.add(db_repository)
    db_connection.commit()
    db_connection.refresh(db_repository)
    return db_repository


def create_repository_if_not_exists(db_connection: Session,
                                    repository: repository_schema.RepositoryCreate):
    # Query the database to see if the repository object exists based on the unique constraint parameters
    db_select_repository = db_connection.query(model.DBrepository) \
        .filter(model.repository.DBrepository.project_key == repository.project_key,
                model.repository.DBrepository.repository_id == repository.repository_id,
                model.repository.DBrepository.vcs_instance == repository.vcs_instance).first()
    if db_select_repository is not None:
        return db_select_repository

    # Create non-existing repository object
    return create_repository(db_connection, repository)


def get_distinct_projects(db_connection: Session, vcs_providers: [VCSProviders] = None, repository_filter: str = ""):
    """
        Retrieve all unique project names
    :param db_connection:
        Session of the database connection
    :param vcs_providers:
        optional, filter of supported vcs provider types
    :param repository_filter:
        optional, filter on repository name. Is used as a string contains filter
    :return: distinct_projects
        The output will contain a list of unique projects
    """
    query = db_connection.query(model.DBrepository.project_key)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if repository_filter:
        query = query.filter(model.DBrepository.repository_name == repository_filter)

    distinct_projects = query.distinct().all()
    return distinct_projects


def get_distinct_repositories(db_connection: Session, vcs_providers: [VCSProviders] = None, project_name: str = ""):
    """
        Retrieve all unique repository names
    :param db_connection:
        Session of the database connection
    :param vcs_providers:
        optional, filter of supported vcs provider types
    :param project_name:
        optional, filter on project name. Is used as a full string match filter
    :return: distinct_repositories
        The output will contain a list of unique repositories
    """
    query = db_connection.query(model.DBrepository.repository_name)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_name:
        query = query.filter(model.DBrepository.project_key == project_name)

    distinct_repositories = query.distinct().all()
    return distinct_repositories


def get_findings_metadata_by_repository_id(db_connection: Session, repository_id: int):
    """
        Retrieves the finding metadata for a repository id from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository for which findings metadata to be retrieved
    :return: findings_metadata
        findings_metadata containing the count for each status
    """
    latest_scan = scan_crud.get_latest_scan_for_repository_for_master_branch(db_connection, repository_id=repository_id)

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


def delete_repository(db_connection: Session, repository_id: int, delete_related: bool = False):
    """
        Delete a repository object
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository to be deleted
    :param delete_related:
        if related records need to be deleted
    """
    if delete_related:
        scan_finding_crud.delete_scan_finding_by_repository_id(db_connection, repository_id=repository_id)
        finding_crud.delete_findings_by_repository_id(db_connection, repository_id=repository_id)
        scan_crud.delete_scans_by_repository_id(db_connection, repository_id=repository_id)
        branch_crud.delete_branches_by_repository_id(db_connection, repository_id=repository_id)
    db_connection.query(model.DBrepository) \
        .filter(model.repository.DBrepository.id_ == repository_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_repositories_by_vcs_instance_id(db_connection: Session, vcs_instance_id: int):
    """
        Delete repositories for a given vcs instance
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the vcs instance
    """
    db_connection.query(model.DBrepository) \
        .filter(model.repository.DBrepository.vcs_instance == model.vcs_instance.DBVcsInstance.id_,
                model.vcs_instance.DBVcsInstance.id_ == vcs_instance_id) \
        .delete(synchronize_session=False)
    db_connection.commit()
