# Standard Library
import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# First Party
from resc_backend.constants import (
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    REPOSITORIES_TAG,
    RWS_ROUTE_BRANCHES,
    RWS_ROUTE_DISTINCT_PROJECTS,
    RWS_ROUTE_DISTINCT_REPOSITORIES,
    RWS_ROUTE_FINDINGS_METADATA,
    RWS_ROUTE_REPOSITORIES
)
from resc_backend.db.connection import Session
from resc_backend.db.model import DBbranch
from resc_backend.resc_web_service.crud import branch as branch_crud
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import repository as repository_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.helpers.resc_swagger_models import Model404
from resc_backend.resc_web_service.schema import branch as branch_schema
from resc_backend.resc_web_service.schema import repository as repository_schema
from resc_backend.resc_web_service.schema import repository_enriched as repository_enriched_schema
from resc_backend.resc_web_service.schema.finding_count_model import FindingCountModel
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel
from resc_backend.resc_web_service.schema.scan_type import ScanType
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(prefix=f"{RWS_ROUTE_REPOSITORIES}", tags=[REPOSITORIES_TAG])


@router.get("",
            response_model=PaginationModel[repository_schema.RepositoryRead],
            summary="Get repositories",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the repositories"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_all_repositories(skip: int = Query(default=0, ge=0),
                         limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                         vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                         projectfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                         repositoryfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                         db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[repository_schema.RepositoryRead]:
    """
        Retrieve all repository objects paginated

    - **db_connection**: Session of the database connection
    - **skip**: Integer amount of records to skip to support pagination
    - **limit**: Integer amount of records to return, to support pagination
    - **vcsproviders**: Optional, filter on supported vcs provider types
    - **projectfilter**: Optional, filter on project name. It is used as a string contains filter
    - **repositoryfilter**: Optional, filter on repository name. It is used as a string contains filter
    - **return**: [RepositoryRead]
        The output will contain a PaginationModel containing the list of RepositoryRead type objects,
        or an empty list if no repository
    """

    repositories = repository_crud.get_repositories(db_connection, skip=skip, limit=limit,
                                                    vcs_providers=vcsproviders,
                                                    project_filter=projectfilter,
                                                    repository_filter=repositoryfilter)

    total_repositories = repository_crud.get_repositories_count(db_connection, vcs_providers=vcsproviders,
                                                                project_filter=projectfilter,
                                                                repository_filter=repositoryfilter)

    return PaginationModel[repository_schema.RepositoryRead](data=repositories, total=total_repositories,
                                                             limit=limit, skip=skip)


@router.post("",
             response_model=repository_schema.RepositoryRead,
             summary="Create a repository",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {"description": "Create a new repository"},
                 500: {"description": ERROR_MESSAGE_500},
                 503: {"description": ERROR_MESSAGE_503}
             })
def create_repository(
        repository: repository_schema.RepositoryCreate,
        db_connection: Session = Depends(get_db_connection)):
    """
        Create a repository with all the information

    - **db_connection**: Session of the database connection
    - **project_key**: each repository must have a project name or key
    - **repository_id**: repository id
    - **repository_name**: repository name
    - **repository_url**: repository url
    - **vcs_instance**: vcs instance id
    """
    return repository_crud.create_repository_if_not_exists(db_connection=db_connection, repository=repository)


@router.get("/{repository_id}",
            response_model=repository_schema.RepositoryRead,
            summary="Fetch a repository by ID",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve repository <repository_id>"},
                404: {"model": Model404, "description": "Repository <repository_id> not found"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def read_repository(repository_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Read a repository by ID

    - **db_connection**: Session of the database connection
    - **repository_id**: ID of the repository for which details need to be fetched
    """
    db_repository = repository_crud.get_repository(db_connection, repository_id=repository_id)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return db_repository


@router.put("/{repository_id}",
            response_model=repository_schema.RepositoryRead,
            summary="Update an existing repository",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Update repository <repository_id>"},
                404: {"model": Model404, "description": "Repository <repository_id> not found"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def update_repository(
        repository_id: int,
        repository: repository_schema.RepositoryCreate,
        db_connection: Session = Depends(get_db_connection)
):
    """
        Update an existing repository

    - **db_connection**: Session of the database connection
    - **repository_id**: ID of the repository
    - **project_key**: project name that needs to be updated
    - **repository_id**: repository id that needs to be updated
    - **repository_name**: repository name that needs to be updated
    - **repository_url**: repository url that needs to be updated
    - **vcs_instance**: vcs instance id that needs to be updated
    """
    db_repository = repository_crud.get_repository(db_connection, repository_id=repository_id)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repository_crud.update_repository(
        db_connection=db_connection, repository_id=repository_id, repository=repository)


@router.delete("/{repository_id}",
               summary="Delete a repository",
               status_code=status.HTTP_200_OK,
               responses={
                   200: {"description": "Delete repository <repository_id>"},
                   404: {"model": Model404, "description": "Repository <repository_id> not found"},
                   500: {"description": ERROR_MESSAGE_500},
                   503: {"description": ERROR_MESSAGE_503}
               })
def delete_repository(repository_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Delete a repository

    - **db_connection**: Session of the database connection
    - **repository_id**: ID of the repository to delete
    - **return**: The output will contain a success or error message based on the success of the deletion
    """
    db_repository = repository_crud.get_repository(db_connection, repository_id=repository_id)
    if db_repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    repository_crud.delete_repository(db_connection, repository_id=repository_id, delete_related=True)
    return {"ok": True}


@router.get("/{repository_id}"f"{RWS_ROUTE_BRANCHES}",
            response_model=PaginationModel[branch_schema.ViewableBranch],
            summary="Get branches for a repository",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the branches of a repository, enriched with the recent scan "
                                     "information"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_branches_for_repository(repository_id: int, skip: int = Query(default=0, ge=0),
                                limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                                db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[branch_schema.ViewableBranch]:
    """
        Retrieve all branches enriched with most recent scan information for a repository

    - **db_connection**: Session of the database connection
    - **repository_id**: ID of the parent repository object for which branch objects need to be retrieved
    - **skip**: Integer amount of records to skip to support pagination
    - **limit**: Integer amount of records to return, to support pagination
    - **return**: [ViewableBranch]
        The output will contain a PaginationModel containing the list of ViewableBranch type objects,
        or an empty list if no branch was found for the given repository_id
    """
    branches = branch_crud.get_branches_for_repository(db_connection, skip=skip, limit=limit,
                                                       repository_id=repository_id)
    for branch in branches:
        branch = enrich_branch_with_latest_scan_data(db_connection, branch)

    total_branches = branch_crud.get_branches_count_for_repository(db_connection,
                                                                   repository_id=repository_id)
    return PaginationModel[branch_schema.ViewableBranch](data=branches, total=total_branches,
                                                         limit=limit, skip=skip)


def enrich_branch_with_latest_scan_data(db_connection: Session, branch: DBbranch):
    """
        Enriches a branch object retrieved from the database with most recent scan information
    :param db_connection:
        Session of the database connection
    :param branch:
        DBbranch object to enrich with scan information
    :return: branch
        DBbranch object enriched with latest scan information as type ViewableBranch
    """

    branch.last_scan_datetime = datetime.datetime.min
    branch.last_scan_id = None
    branch.last_scan_finding_count = 0
    branch.scan_finding_count = 0

    latest_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_id=branch.id_)
    if latest_scan is not None:
        branch.last_scan_datetime = latest_scan.timestamp
        branch.last_scan_id = latest_scan.id_
        branch.last_scan_finding_count = finding_crud.get_total_findings_count(
            db_connection, FindingsFilter(scan_ids=[latest_scan.id_]))

        scan_ids_latest_to_base = []
        scans = scan_crud.get_scans(db_connection=db_connection, branch_id=branch.id_, limit=1000000)
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
            summary="Get all unique project names",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the unique project-names"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_distinct_projects(vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                          repositoryfilter: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                          onlyifhasfindings: bool = Query(default=False),
                          db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all unique project names

    - **db_connection**: Session of the database connection
    - **vcsproviders**: Optional, filter on supported vcs provider types
    - **repositoryfilter**: Optional, filter on repository name. It is used as a string contains filter
    - **onlyifhasfindings**: Optional, filter all projects those have findings
    - **return**: List[str]
        The output will contain a list of unique projects
    """

    distinct_projects = repository_crud.get_distinct_projects(db_connection,
                                                              vcs_providers=vcsproviders,
                                                              repository_filter=repositoryfilter,
                                                              only_if_has_findings=onlyifhasfindings)
    projects = [project.project_key for project in distinct_projects]
    return projects


@router.get(f"{RWS_ROUTE_DISTINCT_REPOSITORIES}/",
            response_model=List[str],
            summary="Get all unique repository names",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the unique repository names"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_distinct_repositories(vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
                              projectname: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
                              onlyifhasfindings: bool = Query(default=False),
                              db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all unique repository names

    - **db_connection**: Session of the database connection
    - **vcsproviders**: Optional, filter of supported vcs provider types
    - **projectname**: Optional, filter on project name. It is used as a full string match filter
    - **onlyifhasfindings**: Optional, filter all repositories that have findings
    - **return**: List[str]
        The output will contain a list of unique repositories
    """

    distinct_repositories = repository_crud.get_distinct_repositories(db_connection,
                                                                      vcs_providers=vcsproviders,
                                                                      project_name=projectname,
                                                                      only_if_has_findings=onlyifhasfindings)
    repositories = [repo.repository_name for repo in distinct_repositories]
    return repositories


@router.get("/{repository_id}"f"{RWS_ROUTE_FINDINGS_METADATA}",
            response_model=FindingCountModel[repository_schema.RepositoryRead],
            summary="Get findings metadata for a repository",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve findings metadata for repository <repository_id>"},
                404: {"model": Model404, "description": "Repository <repository_id> not found"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_findings_metadata_for_repository(repository_id: int,
                                         db_connection: Session = Depends(get_db_connection)) \
        -> FindingCountModel[repository_schema.RepositoryRead]:
    """
        Retrieve findings metadata for a repository

    - **db_connection**: Session of the database connection
    - **repository_id**: ID of the repository object for which findings metadata to be retrieved
    - **return**: RepositoryRead, findings count per status
        The output will contain a RepositoryRead type object along with findings count per status,
        or empty if no scan was found
    """
    repository = repository_crud.get_repository(db_connection, repository_id=repository_id)
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    findings_meta_data = repository_crud.get_findings_metadata_by_repository_id(
        db_connection, repository_ids=[repository_id])

    return FindingCountModel[repository_schema.RepositoryRead](
        data=repository,
        true_positive=findings_meta_data[repository_id]["true_positive"],
        false_positive=findings_meta_data[repository_id]["false_positive"],
        not_analyzed=findings_meta_data[repository_id]["not_analyzed"],
        under_review=findings_meta_data[repository_id]["under_review"],
        clarification_required=findings_meta_data[repository_id]["clarification_required"],
        total_findings_count=findings_meta_data[repository_id]["total_findings_count"])


@router.get(f"{RWS_ROUTE_FINDINGS_METADATA}/",
            response_model=PaginationModel[repository_enriched_schema.RepositoryEnrichedRead],
            summary="Get all repositories with findings metadata",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the findings metadata for all the repositories"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_all_repositories_with_findings_metadata(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
        vcsproviders: List[VCSProviders] = Query(None, alias="vcsprovider",
                                                 title="VCSProviders"),
        projectfilter: Optional[str] = Query('',
                                             regex=r"^[A-z0-9 .\-_%]*$"),
        repositoryfilter: Optional[str] = Query('',
                                                regex=r"^[A-z0-9 .\-_%]*$"),
        onlyifhasfindings: bool = Query(default=False),
        db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[repository_enriched_schema.RepositoryEnrichedRead]:
    """
        Retrieve all repository objects paginated

    - **db_connection**: Session of the database connection
    - **skip**: Integer amount of records to skip to support pagination
    - **limit**: Integer amount of records to return, to support pagination
    - **vcsproviders**: Optional, filter on supported vcs provider types
    - **projectfilter**: Optional, filter on project name. It is used as a string contains filter
    - **repositoryfilter**: Optional, filter on repository name. It is used as a string contains filter
    - **onlyifhasfindings**: Optional, filter all repositories those have findings
    - **return**: [RepositoryEnrichedRead]
        The output will contain a PaginationModel containing the list of RepositoryEnrichedRead type objects,
        or an empty list if no repository
    """

    repositories = repository_crud.get_repositories(db_connection, skip=skip, limit=limit,
                                                    vcs_providers=vcsproviders,
                                                    project_filter=projectfilter,
                                                    repository_filter=repositoryfilter,
                                                    only_if_has_findings=onlyifhasfindings)

    total_repositories = repository_crud.get_repositories_count(db_connection, vcs_providers=vcsproviders,
                                                                project_filter=projectfilter,
                                                                repository_filter=repositoryfilter,
                                                                only_if_has_findings=onlyifhasfindings)
    repository_list = []
    repo_ids = [repo.id_ for repo in repositories]
    repo_findings_meta_data = repository_crud.get_findings_metadata_by_repository_id(
        db_connection, repository_ids=repo_ids)
    for repo in repositories:
        enriched_repository = repository_enriched_schema.RepositoryEnrichedRead(
            id_=repo.id_,
            project_key=repo.project_key,
            repository_id=repo.repository_id,
            repository_name=repo.repository_name,
            repository_url=repo.repository_url,
            vcs_provider=repo.provider_type,
            true_positive=repo_findings_meta_data[repo.id_]["true_positive"],
            false_positive=repo_findings_meta_data[repo.id_]["false_positive"],
            not_analyzed=repo_findings_meta_data[repo.id_]["not_analyzed"],
            under_review=repo_findings_meta_data[repo.id_]["under_review"],
            clarification_required=repo_findings_meta_data[repo.id_]["clarification_required"],
            total_findings_count=repo_findings_meta_data[repo.id_]["total_findings_count"]
        )
        repository_list.append(enriched_repository)

    return PaginationModel[repository_enriched_schema.RepositoryEnrichedRead](data=repository_list,
                                                                              total=total_repositories,
                                                                              limit=limit, skip=skip)
