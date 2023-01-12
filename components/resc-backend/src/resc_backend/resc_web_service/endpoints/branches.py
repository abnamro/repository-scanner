# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# First Party
from resc_backend.constants import (
    BRANCHES_TAG,
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    RWS_ROUTE_BRANCHES,
    RWS_ROUTE_FINDINGS_METADATA,
    RWS_ROUTE_LAST_SCAN,
    RWS_ROUTE_SCANS
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import branch as branch_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.helpers.resc_swagger_models import Model404
from resc_backend.resc_web_service.schema import branch as branch_schema
from resc_backend.resc_web_service.schema import scan as scan_schema
from resc_backend.resc_web_service.schema.finding_count_model import FindingCountModel
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel

router = APIRouter(prefix=f"{RWS_ROUTE_BRANCHES}", tags=[BRANCHES_TAG])


@router.get("",
            response_model=PaginationModel[branch_schema.BranchRead],
            summary="Get branches",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all branches"}
            })
def get_all_branches(skip: int = Query(default=0, ge=0),
                     limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                     db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[branch_schema.BranchRead]:
    """
        Retrieve all branch objects paginated

    - **db_connection**: Session of the database connection
    - **skip**: Integer amount of records to skip to support pagination
    - **limit**: Integer amount of records to return, to support pagination
    - **return**: [BranchRead]
        The output will contain a PaginationModel containing the list of BranchRead type objects,
        or an empty list if no branch was found
    """
    branches = branch_crud.get_branches(db_connection, skip=skip, limit=limit)

    total_branches = branch_crud.get_branches_count(db_connection)

    return PaginationModel[branch_schema.BranchRead](data=branches, total=total_branches,
                                                     limit=limit, skip=skip)


@router.post("",
             response_model=branch_schema.BranchRead,
             summary="Create a branch",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {"description": "Create a new branch"}
             })
def create_branch(
        branch: branch_schema.BranchCreate, db_connection: Session = Depends(get_db_connection)):
    """
        Create a branch with all the information

    - **db_connection**: Session of the database connection
    - **branch_id**: branch id
    - **branch_name**: branch name
    - **latest_commit**: branch latest commit hash
    - **repository_id**: repository id
    """
    return branch_crud.create_branch_if_not_exists(db_connection=db_connection, branch=branch)


@router.get("/{branch_id}",
            response_model=branch_schema.BranchRead,
            summary="Fetch a branch by ID",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve branch <branch_id>"},
                404: {"model": Model404, "description": "Branch <branch_id> not found"}
            })
def read_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Read a branch by ID

    - **db_connection**: Session of the database connection
    - **branch_id**: ID of the branch for which details need to be fetched
    """
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch


@router.put("/{branch_id}",
            response_model=branch_schema.BranchRead,
            summary="Update an existing branch",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Update branch <branch_id>"},
                404: {"model": Model404, "description": "Branch <branch_id> not found"}
            })
def update_branch(
        branch_id: int,
        branch: branch_schema.BranchCreate,
        db_connection: Session = Depends(get_db_connection)):
    """
        Update an existing branch

    - **db_connection**: Session of the database connection
    - **branch_id**: branch id to update
    - **branch_name**: branch name to update
    - **latest_commit**: branch latest commit hash to update
    - **repository_id**: repository id to update
    """
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch_crud.update_branch(
        db_connection=db_connection,
        branch_id=branch_id,
        branch=branch
    )


@router.delete("/{branch_id}",
               summary="Delete a branch",
               status_code=status.HTTP_200_OK,
               responses={
                   200: {"description": "Delete branch <branch_id>"},
                   404: {"model": Model404, "description": "Branch <branch_id> not found"}
               })
def delete_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Delete a branch object

    - **db_connection**: Session of the database connection
    - **branch_id**: ID of the branch to delete
    - **return**: The output will contain a success or error message based on the success of the deletion
    """
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    branch_crud.delete_branch(db_connection, branch_id=branch_id, delete_related=True)
    return {"ok": True}


@router.get("/{branch_id}"f"{RWS_ROUTE_SCANS}",
            summary="Get scans for branch",
            response_model=PaginationModel[scan_schema.ScanRead],
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the scans related to a branch"}
            })
def get_scans_for_branch(branch_id: int, skip: int = Query(default=0, ge=0),
                         limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                         db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[scan_schema.ScanRead]:
    """
        Retrieve all scan objects related to a branch paginated

    - **db_connection**: Session of the database connection
    - **branch_id**: ID of the parent branch object for which scan objects to be retrieved
    - **skip**: Integer amount of records to skip to support pagination
    - **limit**: Integer amount of records to return, to support pagination
    - **return**: [ScanRead]
        The output will contain a PaginationModel containing the list of ScanRead type objects,
        or an empty list if no scan was found
    """
    scans = scan_crud.get_scans(db_connection, skip=skip, limit=limit, branch_id=branch_id)

    total_scans = scan_crud.get_scans_count(db_connection, branch_id=branch_id)

    return PaginationModel[scan_schema.ScanRead](data=scans, total=total_scans, limit=limit, skip=skip)


@router.get("/{branch_id}"f"{RWS_ROUTE_LAST_SCAN}",
            response_model=scan_schema.ScanRead,
            summary="Get latest scan for branch",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve the latest scan related to a branch"}
            })
def get_last_scan_for_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)) \
        -> scan_schema.ScanRead:
    """
        Retrieve the latest scan object related to a branch

    - **db_connection**: Session of the database connection
    - **branch_id**: ID of the parent branch object for which scan objects to be retrieved
    - **return**: ScanRead
        The output will contain a ScanRead type object,
        or empty if no scan was found
    """
    last_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_id=branch_id)

    return last_scan


@router.get("/{branch_id}"f"{RWS_ROUTE_FINDINGS_METADATA}",
            response_model=FindingCountModel[branch_schema.BranchRead],
            summary="Get findings metadata for branch",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve findings metadata for branch <branch_id>"},
                404: {"model": Model404, "description": "Branch <branch_id> not found"}
            })
def get_findings_metadata_for_branch(branch_id: int,
                                     db_connection: Session = Depends(get_db_connection)) \
        -> FindingCountModel[branch_schema.BranchRead]:
    """
        Retrieve findings metadata for a branch

    - **db_connection**: Session of the database connection
    - **branch_id**: ID of the branch object for which findings metadata to be retrieved
    - **return**: BranchedRead, findings count per status
        The output will contain a BranchedRead type object along with findings count per status,
        or empty if no scan was found
    """
    branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    findings_meta_data = branch_crud.get_findings_metadata_by_branch_id(db_connection,
                                                                        branch_id=branch_id)

    return FindingCountModel[branch_schema.BranchRead](
        data=branch,
        true_positive=findings_meta_data["true_positive"],
        false_positive=findings_meta_data["false_positive"],
        not_analyzed=findings_meta_data["not_analyzed"],
        under_review=findings_meta_data["under_review"],
        clarification_required=findings_meta_data["clarification_required"],
        total_findings_count=findings_meta_data["total_findings_count"])
