# pylint:disable=not-callable
# Third Party
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.crud import scan_finding as scan_finding_crud
from resc_backend.resc_web_service.schema import repository as repository_schema
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.scan_type import ScanType
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


def get_repositories(db_connection: Session, vcs_providers: [VCSProviders] = None, skip: int = 0,
                     limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT, project_filter: str = "",
                     repository_filter: str = "", only_if_has_findings: bool = False):
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
    :param only_if_has_findings:
        optional, filter on repositories with findings
    :return: repositories
        list of DBrepository objects
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit

    # Get the latest scan for repository
    repo_last_scan_sub_query = db_connection.query(model.DBscan.repository_id,
                                                   func.max(model.DBscan.timestamp).label("max_timestamp"))
    repo_last_scan_sub_query = repo_last_scan_sub_query.group_by(model.DBscan.repository_id).subquery()

    query = db_connection.query(
        model.DBrepository.id_,
        model.DBrepository.project_key,
        model.DBrepository.repository_id,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
        model.DBrepository.vcs_instance,
        model.DBVcsInstance.provider_type,
        func.coalesce(model.DBscan.id_, None).label('last_scan_id'),
        func.coalesce(model.DBscan.timestamp, None).label('last_scan_timestamp'))
    query = query.join(model.DBVcsInstance,
                       model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
    query = query.join(repo_last_scan_sub_query,
                       model.repository.DBrepository.id_ == repo_last_scan_sub_query.c.repository_id, isouter=True)
    query = query.join(model.DBscan,
                       and_(model.scan.DBscan.repository_id == repo_last_scan_sub_query.c.repository_id,
                            model.scan.DBscan.timestamp == repo_last_scan_sub_query.c.max_timestamp), isouter=True)

    if only_if_has_findings:
        max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                     func.max(model.DBscan.id_).label("latest_base_scan_id"))
        max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
        max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

        sub_query = db_connection.query(model.DBrepository.id_)
        sub_query = sub_query.join(max_base_scan_subquery,
                                   model.DBrepository.id_ == max_base_scan_subquery.c.repository_id)
        sub_query = sub_query.join(model.DBscan, and_(model.DBrepository.id_ == model.DBscan.repository_id,
                                                      model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
        sub_query = sub_query.join(model.DBscanFinding, model.DBscan.id_ == model.DBscanFinding.scan_id)
        sub_query = sub_query.distinct()

        # Filter on repositories that are in the selection
        query = query.filter(model.DBrepository.id_.in_(sub_query))

    if vcs_providers and vcs_providers is not None:
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_filter:
        query = query.filter(model.DBrepository.project_key == project_filter)

    if repository_filter:
        query = query.filter(model.DBrepository.repository_name == repository_filter)

    repositories = query.order_by(model.DBrepository.id_).offset(skip).limit(limit_val).all()

    return repositories


def get_repositories_count(db_connection: Session, vcs_providers: [VCSProviders] = None, project_filter: str = "",
                           repository_filter: str = "", only_if_has_findings: bool = False) -> int:
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
    :param only_if_has_findings:
        optional, filter on repositories with findings
    :return: total_count
        count of repositories
    """
    query = db_connection.query(func.count(model.DBrepository.id_))

    if only_if_has_findings:
        max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                     func.max(model.DBscan.id_).label("latest_base_scan_id"))
        max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
        max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

        sub_query = db_connection.query(model.DBrepository.id_)
        sub_query = sub_query.join(max_base_scan_subquery,
                                   model.DBrepository.id_ == max_base_scan_subquery.c.repository_id)
        sub_query = sub_query.join(model.DBscan, and_(model.DBrepository.id_ == model.DBscan.repository_id,
                                                      model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
        sub_query = sub_query.join(model.DBscanFinding, model.DBscan.id_ == model.DBscanFinding.scan_id)
        sub_query = sub_query.distinct()

        # Filter on repositories that are in the selection
        query = query.filter(model.DBrepository.id_.in_(sub_query))

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


def get_distinct_projects(db_connection: Session, vcs_providers: [VCSProviders] = None, repository_filter: str = "",
                          only_if_has_findings: bool = False):
    """
        Retrieve all unique project names
    :param db_connection:
        Session of the database connection
    :param vcs_providers:
        optional, filter of supported vcs provider types
    :param repository_filter:
        optional, filter on repository name. Is used as a string contains filter
    :param only_if_has_findings:
        optional, filter on repositories that have findings
    :return: distinct_projects
        The output will contain a list of unique projects
    """
    query = db_connection.query(model.DBrepository.project_key)

    if only_if_has_findings:
        max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                     func.max(model.DBscan.id_).label("latest_base_scan_id"))
        max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
        max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

        query = query.join(max_base_scan_subquery, model.DBrepository.id_ == max_base_scan_subquery.c.repository_id)
        query = query.join(model.DBscan, and_(model.DBrepository.id_ == model.DBscan.repository_id,
                                              model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
        query = query.join(model.DBscanFinding, model.DBscan.id_ == model.DBscanFinding.scan_id)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if repository_filter:
        query = query.filter(model.DBrepository.repository_name == repository_filter)

    distinct_projects = query.distinct().all()
    return distinct_projects


def get_distinct_repositories(db_connection: Session, vcs_providers: [VCSProviders] = None, project_name: str = "",
                              only_if_has_findings: bool = False):
    """
        Retrieve all unique repository names
    :param db_connection:
        Session of the database connection
    :param vcs_providers:
        optional, filter of supported vcs provider types
    :param project_name:
        optional, filter on project name. Is used as a full string match filter
    :param only_if_has_findings:
        optional, filter on repositories that have findings
    :return: distinct_repositories
        The output will contain a list of unique repositories
    """
    query = db_connection.query(model.DBrepository.repository_name)

    if only_if_has_findings:
        max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                     func.max(model.DBscan.id_).label("latest_base_scan_id"))
        max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
        max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

        query = query.join(max_base_scan_subquery, model.DBrepository.id_ == max_base_scan_subquery.c.repository_id)
        query = query.join(model.DBscan, and_(model.DBrepository.id_ == model.DBscan.repository_id,
                                              model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
        query = query.join(model.DBscanFinding, model.DBscan.id_ == model.DBscanFinding.scan_id)

    if vcs_providers and vcs_providers is not None:
        query = query.join(model.DBVcsInstance,
                           model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

    if project_name:
        query = query.filter(model.DBrepository.project_key == project_name)

    distinct_repositories = query.distinct().all()
    return distinct_repositories


def get_findings_metadata_by_repository_id(db_connection: Session, repository_ids: list[int]):
    """
        Retrieves the finding metadata for a repository id from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param repository_ids:
        ids of the repository for which findings metadata to be retrieved
    :return: findings_metadata
        findings_metadata containing the count for each status
    """
    query = db_connection.query(model.DBrepository.id_,
                                model.DBaudit.status,
                                func.count(model.DBscanFinding.finding_id))

    max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                 func.max(model.DBscan.id_).label("latest_base_scan_id"))
    max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
    max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

    max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                             func.max(model.DBaudit.id_).label("audit_id")) \
        .group_by(model.DBaudit.finding_id).subquery()

    query = query.join(max_base_scan_subquery, model.DBrepository.id_ == max_base_scan_subquery.c.repository_id)
    query = query.join(model.DBscan, and_(model.DBrepository.id_ == model.DBscan.repository_id,
                                          model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
    query = query.join(model.DBscanFinding, model.DBscan.id_ == model.DBscanFinding.scan_id)
    query = query.join(max_audit_subquery, max_audit_subquery.c.finding_id == model.DBscanFinding.finding_id,
                       isouter=True)
    query = query.join(model.DBaudit, and_(model.audit.DBaudit.finding_id == model.DBscanFinding.finding_id,
                                           model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id), isouter=True)
    query = query.filter(model.DBrepository.id_.in_(repository_ids))
    query = query.group_by(model.DBrepository.id_, model.DBaudit.status, )
    status_counts = query.all()
    repo_count_dict = {}
    for repository_id in repository_ids:
        repo_count_dict[repository_id] = {
            "true_positive": 0,
            "false_positive": 0,
            "not_analyzed": 0,
            "under_review": 0,
            "clarification_required": 0,
            "total_findings_count": 0
        }
    for status_count in status_counts:
        repo_count_dict[status_count[0]]["total_findings_count"] += status_count[2]
        if status_count[1] == FindingStatus.NOT_ANALYZED or status_count[1] is None:
            repo_count_dict[status_count[0]]["not_analyzed"] += status_count[2]
        elif status_count[1] == FindingStatus.FALSE_POSITIVE:
            repo_count_dict[status_count[0]]["false_positive"] += status_count[2]
        elif status_count[1] == FindingStatus.TRUE_POSITIVE:
            repo_count_dict[status_count[0]]["true_positive"] += status_count[2]
        elif status_count[1] == FindingStatus.UNDER_REVIEW:
            repo_count_dict[status_count[0]]["under_review"] += status_count[2]
        elif status_count[1] == FindingStatus.CLARIFICATION_REQUIRED:
            repo_count_dict[status_count[0]]["clarification_required"] += status_count[2]

    return repo_count_dict


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
