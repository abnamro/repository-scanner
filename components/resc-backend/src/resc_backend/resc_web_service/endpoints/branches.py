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
from resc_backend.resc_web_service.schema import branch as branch_schema
from resc_backend.resc_web_service.schema import scan as scan_schema
from resc_backend.resc_web_service.schema.finding_count_model import FindingCountModel
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel

router = APIRouter(prefix=f"{RWS_ROUTE_BRANCHES}", tags=[BRANCHES_TAG])


@router.get("",
            response_model=PaginationModel[branch_schema.BranchRead],
            status_code=status.HTTP_200_OK)
def get_all_branches(skip: int = Query(default=0, ge=0),
                     limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                     db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[branch_schema.BranchRead]:
    """
        Retrieve all branch objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [BranchRead]
        The output will contain a PaginationModel containing the list of BranchRead type objects,
        or an empty list if no branch was found
    """
    branches = branch_crud.get_branches(db_connection, skip=skip, limit=limit)

    total_branches = branch_crud.get_branches_count(db_connection)

    return PaginationModel[branch_schema.BranchRead](data=branches, total=total_branches,
                                                     limit=limit, skip=skip)


@router.post("",
             response_model=branch_schema.BranchRead, status_code=status.HTTP_201_CREATED)
def create_branch(
        branch: branch_schema.BranchCreate, db_connection: Session = Depends(get_db_connection)):
    return branch_crud.create_branch_if_not_exists(db_connection=db_connection, branch=branch)


@router.get("/{branch_id}",
            response_model=branch_schema.BranchRead,
            status_code=status.HTTP_200_OK)
def read_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)):
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch


@router.put("/{branch_id}",
            response_model=branch_schema.BranchRead,
            status_code=status.HTTP_200_OK)
def update_branch(
        branch_id: int,
        branch: branch_schema.BranchCreate,
        db_connection: Session = Depends(get_db_connection)
):
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch_crud.update_branch(
        db_connection=db_connection,
        branch_id=branch_id,
        branch=branch
    )


@router.delete("/{branch_id}",
               status_code=status.HTTP_200_OK)
def delete_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Delete a branch object
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch to delete
    :return:
        The output will contain a success or error message based on the success of the deletion
    """
    db_branch = branch_crud.get_branch(db_connection, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    branch_crud.delete_scan_finding_by_branch_id(db_connection, branch_id=branch_id)
    branch_crud.delete_findings_by_branch_id(db_connection, branch_id=branch_id)
    branch_crud.delete_scans_by_branch_id(db_connection, branch_id=branch_id)
    branch_crud.delete_branch(db_connection, branch_id=branch_id)
    return {"ok": True}


@router.get("/{branch_id}"f"{RWS_ROUTE_SCANS}",
            response_model=PaginationModel[scan_schema.ScanRead],
            status_code=status.HTTP_200_OK)
def get_scans_for_branch(branch_id: int, skip: int = Query(default=0, ge=0),
                         limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                         db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[scan_schema.ScanRead]:
    """
        Retrieve all scan objects related to a branch paginated
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the parent branch object of which to retrieve scan objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [ScanRead]
        The output will contain a PaginationModel containing the list of ScanRead type objects,
        or an empty list if no scan was found
    """
    scans = scan_crud.get_scans(db_connection, skip=skip, limit=limit, branch_id=branch_id)

    total_scans = scan_crud.get_scans_count(db_connection, branch_id=branch_id)

    return PaginationModel[scan_schema.ScanRead](data=scans, total=total_scans, limit=limit, skip=skip)


@router.get("/{branch_id}"f"{RWS_ROUTE_LAST_SCAN}",
            response_model=scan_schema.ScanRead,
            status_code=status.HTTP_200_OK)
def get_last_scan_for_branch(branch_id: int, db_connection: Session = Depends(get_db_connection)) \
        -> scan_schema.ScanRead:
    """
        Retrieve latest scan object related to a branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the parent branch object of which to retrieve scan object
    :return: ScanRead
        The output will contain a ScanRead type object,
        or empty if no scan was found
    """
    last_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_id=branch_id)

    return last_scan


@router.get("/{branch_id}"f"{RWS_ROUTE_FINDINGS_METADATA}",
            response_model=FindingCountModel[branch_schema.BranchRead],
            status_code=status.HTTP_200_OK)
def get_findings_metadata_for_branch(branch_id: int,
                                     db_connection: Session = Depends(get_db_connection)) \
        -> FindingCountModel[branch_schema.BranchRead]:
    """
        Retrieve findings metadata for a branch
    :param branch_id:
        id of the branch object for which findings metadata to be retrieved
    :param db_connection:
        Session of the database connection
    :return: BranchedRead, findings count per status
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
