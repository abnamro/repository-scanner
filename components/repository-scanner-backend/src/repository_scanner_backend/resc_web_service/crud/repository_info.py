# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from repository_scanner_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from repository_scanner_backend.db import model
from repository_scanner_backend.resc_web_service.crud import scan as scan_crud
from repository_scanner_backend.resc_web_service.schema import repository_info as repositoryInfo_schema
from repository_scanner_backend.resc_web_service.schema.vcs_provider import VCSProviders


def get_repositories_info(db_connection: Session, vcs_providers: [VCSProviders] = None, skip: int = 0,
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
    :return: repositories_info
        list of DBrepositoryInfo objects
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(
        model.DBrepositoryInfo.id_,
        model.DBrepositoryInfo.project_key,
        model.DBrepositoryInfo.repository_id,
        model.DBrepositoryInfo.repository_name,
        model.DBrepositoryInfo.repository_url,
        model.DBrepositoryInfo.vcs_instance,
        model.DBVcsInstance.provider_type) \
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)

    if vcs_providers and vcs_providers is not None:
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_filter:
        query = query.filter(model.DBrepositoryInfo.project_key == project_filter)

    if repository_filter:
        query = query.filter(model.DBrepositoryInfo.repository_name == repository_filter)

    repositories_info = query.order_by(model.DBrepositoryInfo.id_).offset(skip).limit(limit_val).all()
    return repositories_info


def get_repositories_info_count(db_connection: Session, vcs_providers: [VCSProviders] = None, project_filter: str = "",
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
    query = db_connection.query(func.count(model.DBrepositoryInfo.id_))

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_filter:
        query = query.filter(model.DBrepositoryInfo.project_key == project_filter)

    if repository_filter:
        query = query.filter(model.DBrepositoryInfo.repository_name == repository_filter)

    total_count = query.scalar()
    return total_count


def get_repository_info(db_connection: Session, repository_info_id: int):
    repository_info = db_connection.query(model.DBrepositoryInfo) \
        .filter(model.repository_info.DBrepositoryInfo.id_ == repository_info_id).first()
    return repository_info


def update_repository_info(
        db_connection: Session, repository_info_id: int, repository_info: repositoryInfo_schema.RepositoryInfoCreate):
    db_repository_info = db_connection.query(model.DBrepositoryInfo).filter_by(id_=repository_info_id).first()

    db_repository_info.repository_name = repository_info.repository_name
    db_repository_info.repository_url = repository_info.repository_url
    db_repository_info.vcs_instance = repository_info.vcs_instance

    db_connection.commit()
    db_connection.refresh(db_repository_info)
    return db_repository_info


def create_repository_info(db_connection: Session, repository_info: repositoryInfo_schema.RepositoryInfoCreate):
    db_repository_info = model.repository_info.DBrepositoryInfo(
        project_key=repository_info.project_key,
        repository_id=repository_info.repository_id,
        repository_name=repository_info.repository_name,
        repository_url=repository_info.repository_url,
        vcs_instance=repository_info.vcs_instance
    )
    db_connection.add(db_repository_info)
    db_connection.commit()
    db_connection.refresh(db_repository_info)
    return db_repository_info


def create_repository_info_if_not_exists(db_connection: Session,
                                         repository_info: repositoryInfo_schema.RepositoryInfoCreate):
    # Query the database to see if the repository_info object exists based on the unique constraint parameters
    db_select_repository_info = db_connection.query(model.DBrepositoryInfo) \
        .filter(model.repository_info.DBrepositoryInfo.project_key == repository_info.project_key,
                model.repository_info.DBrepositoryInfo.repository_id == repository_info.repository_id,
                model.repository_info.DBrepositoryInfo.vcs_instance == repository_info.vcs_instance).first()
    if db_select_repository_info is not None:
        return db_select_repository_info

    # Create non-existing repository_info object
    return create_repository_info(db_connection, repository_info)


def delete_repository_info(db_connection: Session, repository_info_id: int):
    db_repository_info = db_connection.query(model.DBrepositoryInfo).filter_by(id_=repository_info_id).first()
    db_connection.delete(db_repository_info)
    db_connection.commit()
    return db_repository_info


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
    query = db_connection.query(model.DBrepositoryInfo.project_key)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if repository_filter:
        query = query.filter(model.DBrepositoryInfo.repository_name == repository_filter)

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
    query = db_connection.query(model.DBrepositoryInfo.repository_name)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_name:
        query = query.filter(model.DBrepositoryInfo.project_key == project_name)

    distinct_repositories = query.distinct().all()
    return distinct_repositories


def get_findings_metadata_by_repository_info_id(db_connection: Session, repository_info_id: int):
    """
        Retrieves the finding metadata for a repository id from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param repository_info_id:
        id of the repository for which findings metadata to be retrieved
    :return: findings_metadata
        findings_metadata containing the count for each status
    """
    latest_scan = scan_crud.get_latest_scan_for_repository_for_master_branch(db_connection,
                                                                             repository_info_id=repository_info_id)

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
