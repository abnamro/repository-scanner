# Standard Library
import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# First Party
from repository_scanner_backend.constants import (
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    REPOSITORIES_TAG,
    RWS_ROUTE_BRANCHES_INFO,
    RWS_ROUTE_DISTINCT_PROJECTS,
    RWS_ROUTE_DISTINCT_REPOSITORIES,
    RWS_ROUTE_FINDINGS_METADATA,
    RWS_ROUTE_REPOSITORIES_INFO
)
from repository_scanner_backend.db.connection import Session
from repository_scanner_backend.db.model import DBbranchInfo
from repository_scanner_backend.resc_web_service.crud import branch_info as branch_info_crud
from repository_scanner_backend.resc_web_service.crud import finding as finding_crud
from repository_scanner_backend.resc_web_service.crud import repository_info as repository_info_crud
from repository_scanner_backend.resc_web_service.crud import scan as scan_crud
from repository_scanner_backend.resc_web_service.dependencies import get_db_connection
from repository_scanner_backend.resc_web_service.filters import FindingsFilter
from repository_scanner_backend.resc_web_service.schema import branch_info as branch_info_schema
from repository_scanner_backend.resc_web_service.schema import repository_info as repository_info_schema
from repository_scanner_backend.resc_web_service.schema import \
    repository_info_enriched as repository_info_enriched_schema
from repository_scanner_backend.resc_web_service.schema.finding_count_model import FindingCountModel
from repository_scanner_backend.resc_web_service.schema.pagination_model import PaginationModel
from repository_scanner_backend.resc_web_service.schema.scan_type import ScanType
from repository_scanner_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(prefix=f"{RWS_ROUTE_REPOSITORIES_INFO}", tags=[REPOSITORIES_TAG])


@router.get("",
            response_model=PaginationModel[repository_info_schema.RepositoryInfoRead],
            status_code=status.HTTP_200_OK)
def get_all_repositories_info(skip: int = Query(default=0, ge=0),
                              limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                              vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                              projectfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                              repositoryfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                              db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[repository_info_schema.RepositoryInfoRead]:
    """
        Retrieve all repository_info objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param vcsproviders:
        optional, filter of supported vcs provider types
    :param projectfilter:
        optional, filter on project name. Is used as a string contains filter
    :param repositoryfilter:
        optional, filter on repository name. Is used as a string contains filter
    :return: [RepositoryInfoRead]
        The output will contain a PaginationModel containing the list of RepositoryInfoRead type objects,
        or an empty list if no repository_info
    """

    repositories_info = repository_info_crud.get_repositories_info(db_connection, skip=skip, limit=limit,
                                                                   vcs_providers=vcsproviders,
                                                                   project_filter=projectfilter,
                                                                   repository_filter=repositoryfilter)

    total_repositories = repository_info_crud.get_repositories_info_count(db_connection, vcs_providers=vcsproviders,
                                                                          project_filter=projectfilter,
                                                                          repository_filter=repositoryfilter)

    return PaginationModel[repository_info_schema.RepositoryInfoRead](data=repositories_info, total=total_repositories,
                                                                      limit=limit, skip=skip)


@router.post("",
             response_model=repository_info_schema.RepositoryInfoRead,
             status_code=status.HTTP_201_CREATED)
def create_repository_info(
        repository_info: repository_info_schema.RepositoryInfoCreate,
        db_connection: Session = Depends(get_db_connection)):
    return repository_info_crud.create_repository_info_if_not_exists(db_connection=db_connection,
                                                                     repository_info=repository_info)


@router.get("/{repository_info_id}",
            response_model=repository_info_schema.RepositoryInfoRead,
            status_code=status.HTTP_200_OK)
def read_repository_info(repository_info_id: int, db_connection: Session = Depends(get_db_connection)):
    db_repository_info = repository_info_crud.get_repository_info(db_connection, repository_info_id=repository_info_id)
    if db_repository_info is None:
        raise HTTPException(status_code=404, detail="RepositoryInfo not found")
    return db_repository_info


@router.put("/{repository_info_id}",
            response_model=repository_info_schema.RepositoryInfoRead,
            status_code=status.HTTP_200_OK)
def update_repository_info(
        repository_info_id: int,
        repository_info: repository_info_schema.RepositoryInfoCreate,
        db_connection: Session = Depends(get_db_connection)
):
    db_repository_info = repository_info_crud.get_repository_info(db_connection, repository_info_id=repository_info_id)
    if db_repository_info is None:
        raise HTTPException(status_code=404, detail="RepositoryInfo not found")
    return repository_info_crud.update_repository_info(
        db_connection=db_connection, repository_info_id=repository_info_id, repository_info=repository_info)


@router.delete("/{repository_info_id}",
               status_code=status.HTTP_200_OK)
def delete_repository_info(repository_info_id: int, db_connection: Session = Depends(get_db_connection)):
    db_repository_info = repository_info_crud.get_repository_info(db_connection, repository_info_id=repository_info_id)
    if db_repository_info is None:
        raise HTTPException(status_code=404, detail="RepositoryInfo not found")
    return repository_info_crud.delete_repository_info(db_connection, repository_info_id)


@router.get("/{repository_info_id}"f"{RWS_ROUTE_BRANCHES_INFO}",
            response_model=PaginationModel[branch_info_schema.ViewableBranchInfo],
            status_code=status.HTTP_200_OK)
def get_branches_info_for_repository(repository_info_id: int, skip: int = Query(default=0, ge=0),
                                     limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                                     db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[branch_info_schema.ViewableBranchInfo]:
    """
        Retrieve all branch_info child objects of a repository_info object from the database
        enriched with most recent scan information
    :param db_connection:
        Session of the database connection
    :param repository_info_id:
        id of the parent repository_info object of which to retrieve branch_info objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [ViewableBranchInfo]
        The output will contain a PaginationModel containing the list of ViewableBranchInfo type objects,
        or an empty list if no branch_info was found for the given repository_info_id
    """
    branches_info = branch_info_crud.get_branches_info_for_repository(db_connection, skip=skip, limit=limit,
                                                                      repository_info_id=repository_info_id)
    for branch in branches_info:
        branch = enrich_branch_with_latest_scan_data(db_connection, branch)

    total_branches = branch_info_crud.get_branches_info_count_for_repository(db_connection,
                                                                             repository_info_id=repository_info_id)
    return PaginationModel[branch_info_schema.ViewableBranchInfo](data=branches_info, total=total_branches,
                                                                  limit=limit, skip=skip)


def enrich_branch_with_latest_scan_data(db_connection: Session, branch: DBbranchInfo):
    """
        Enriches a branch_info object retrieved from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param branch:
        DBbranchInfo object to enrich with scan information
    :return: branch
        DBbranchInfo object enriched with latest scan information as type ViewableBranchInfo
    """

    branch.last_scan_datetime = datetime.datetime.min
    branch.last_scan_id = None
    branch.last_scan_finding_count = 0
    branch.scan_finding_count = 0

    latest_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_info_id=branch.id_)
    if latest_scan is not None:
        branch.last_scan_datetime = latest_scan.timestamp
        branch.last_scan_id = latest_scan.id_
        branch.last_scan_finding_count = finding_crud.get_total_findings_count(
            db_connection, FindingsFilter(scan_ids=[latest_scan.id_]))

        scan_ids_latest_to_base = []
        scans = scan_crud.get_scans(db_connection=db_connection, branch_info_id=branch.id_, limit=1000000)
        scans.sort(key=lambda x: x.timestamp, reverse=True)
        for scan in scans:
            if scan.timestamp <= latest_scan.timestamp:
                scan_ids_latest_to_base.append(scan.id_)
                if scan.scan_type == ScanType.BASE:
                    break

        branch.scan_finding_count = finding_crud.get_total_findings_count(
            db_connection, FindingsFilter(scan_ids=scan_ids_latest_to_base))

    return branch


@router.get(f"{RWS_ROUTE_DISTINCT_PROJECTS}/",
            response_model=List[str],
            status_code=status.HTTP_200_OK)
def get_distinct_projects(vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                          repositoryfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                          db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all unique project names
    :param db_connection:
        Session of the database connection
    :param vcsproviders:
        optional, filter of supported vcs provider types
    :param repositoryfilter:
        optional, filter on repository name. Is used as a string contains filter
    :return: List[str]
        The output will contain a list of unique projects
    """

    distinct_projects = repository_info_crud.get_distinct_projects(db_connection,
                                                                   vcs_providers=vcsproviders,
                                                                   repository_filter=repositoryfilter)
    projects = [project.project_key for project in distinct_projects]
    return projects


@router.get(f"{RWS_ROUTE_DISTINCT_REPOSITORIES}/",
            response_model=List[str],
            status_code=status.HTTP_200_OK)
def get_distinct_repositories(vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                              projectname: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                              db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all unique repository names
    :param db_connection:
        Session of the database connection
    :param vcsproviders:
        optional, filter of supported vcs provider types
    :param projectname:
        optional, filter on project name. Is used as a full string match filter
    :return: List[str]
        The output will contain a list of unique repositories
    """

    distinct_repositories = repository_info_crud.get_distinct_repositories(db_connection,
                                                                           vcs_providers=vcsproviders,
                                                                           project_name=projectname)
    repositories = [repo.repository_name for repo in distinct_repositories]
    return repositories


@router.get("/{repository_info_id}"f"{RWS_ROUTE_FINDINGS_METADATA}",
            response_model=FindingCountModel[repository_info_schema.RepositoryInfoRead],
            status_code=status.HTTP_200_OK)
def get_findings_metadata_for_repository(repository_info_id: int,
                                         db_connection: Session = Depends(get_db_connection)) \
        -> FindingCountModel[repository_info_schema.RepositoryInfoRead]:
    """
        Retrieve findings metadata for a repository
    :param repository_info_id:
        id of the repository_info object for which findings metadata to be retrieved
    :param db_connection:
        Session of the database connection
    :return: RepositoryInfoRead, findings count per status
        The output will contain a RepositoryInfoRead type object along with findings count per status,
        or empty if no scan was found
    """
    repository_info = repository_info_crud.get_repository_info(db_connection, repository_info_id=repository_info_id)
    if repository_info is None:
        raise HTTPException(status_code=404, detail="RepositoryInfo not found")

    findings_meta_data = repository_info_crud.get_findings_metadata_by_repository_info_id(
        db_connection, repository_info_id=repository_info_id)

    return FindingCountModel[repository_info_schema.RepositoryInfoRead](
        data=repository_info,
        true_positive=findings_meta_data["true_positive"],
        false_positive=findings_meta_data["false_positive"],
        not_analyzed=findings_meta_data["not_analyzed"],
        under_review=findings_meta_data["under_review"],
        clarification_required=findings_meta_data["clarification_required"],
        total_findings_count=findings_meta_data["total_findings_count"])


@router.get(f"{RWS_ROUTE_FINDINGS_METADATA}/",
            response_model=PaginationModel[repository_info_enriched_schema.RepositoryInfoEnrichedRead],
            status_code=status.HTTP_200_OK)
def get_all_repositories_info_with_findings_metadata(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
        vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider",
                                                 title="VCSProviders"),
        projectfilter: Optional[str] = Query('',
                                             regex=r"^[A-z0-9 .\-_%]*$"),
        repositoryfilter: Optional[str] = Query('',
                                                regex=r"^[A-z0-9 .\-_%]*$"),
        db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[repository_info_enriched_schema.RepositoryInfoEnrichedRead]:
    """
        Retrieve all repository_info objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param vcsproviders:
        optional, filter of supported vcs provider types
    :param projectfilter:
        optional, filter on project name. Is used as a string contains filter
    :param repositoryfilter:
        optional, filter on repository name. Is used as a string contains filter
    :return: [RepositoryInfoEnrichedRead]
        The output will contain a PaginationModel containing the list of RepositoryInfoEnrichedRead type objects,
        or an empty list if no repository_info
    """

    repositories_info = repository_info_crud.get_repositories_info(db_connection, skip=skip, limit=limit,
                                                                   vcs_providers=vcsproviders,
                                                                   project_filter=projectfilter,
                                                                   repository_filter=repositoryfilter)

    total_repositories = repository_info_crud.get_repositories_info_count(db_connection, vcs_providers=vcsproviders,
                                                                          project_filter=projectfilter,
                                                                          repository_filter=repositoryfilter)
    repository_list = []
    for repo in repositories_info:
        findings_meta_data = repository_info_crud.get_findings_metadata_by_repository_info_id(
            db_connection, repository_info_id=repo.id_)
        enriched_repository = repository_info_enriched_schema.RepositoryInfoEnrichedRead(
            id_=repo.id_,
            project_key=repo.project_key,
            repository_id=repo.repository_id,
            repository_name=repo.repository_name,
            repository_url=repo.repository_url,
            vcs_provider=repo.provider_type,
            true_positive=findings_meta_data["true_positive"],
            false_positive=findings_meta_data["false_positive"],
            not_analyzed=findings_meta_data["not_analyzed"],
            under_review=findings_meta_data["under_review"],
            clarification_required=findings_meta_data["clarification_required"],
            total_findings_count=findings_meta_data["total_findings_count"]
        )
        repository_list.append(enriched_repository)

    return PaginationModel[repository_info_enriched_schema.RepositoryInfoEnrichedRead](data=repository_list,
                                                                                       total=total_repositories,
                                                                                       limit=limit, skip=skip)
