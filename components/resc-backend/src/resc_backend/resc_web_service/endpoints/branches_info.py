# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# First Party
from resc_backend.constants import (
    BRANCHES_TAG,
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    RWS_ROUTE_BRANCHES_INFO,
    RWS_ROUTE_FINDINGS_METADATA,
    RWS_ROUTE_LAST_SCAN,
    RWS_ROUTE_SCANS
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import branch_info as branch_info_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema import branch_info as branch_info_schema
from resc_backend.resc_web_service.schema import scan as scan_schema
from resc_backend.resc_web_service.schema.finding_count_model import FindingCountModel
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel

router = APIRouter(prefix=f"{RWS_ROUTE_BRANCHES_INFO}", tags=[BRANCHES_TAG])


@router.get("",
            response_model=PaginationModel[branch_info_schema.BranchInfoRead],
            status_code=status.HTTP_200_OK)
def get_all_branches_info(skip: int = Query(default=0, ge=0),
                          limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                          db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[branch_info_schema.BranchInfoRead]:
    """
        Retrieve all branch_info objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [BranchInfoRead]
        The output will contain a PaginationModel containing the list of BranchInfoRead type objects,
        or an empty list if no branch_info was found
    """
    branches_info = branch_info_crud.get_branches_info(db_connection, skip=skip, limit=limit)

    total_branches = branch_info_crud.get_branches_info_count(db_connection)

    return PaginationModel[branch_info_schema.BranchInfoRead](data=branches_info, total=total_branches,
                                                              limit=limit, skip=skip)


@router.post("",
             response_model=branch_info_schema.BranchInfoRead, status_code=status.HTTP_201_CREATED)
def create_branch_info(
        branch_info: branch_info_schema.BranchInfoCreate, db_connection: Session = Depends(get_db_connection)):
    return branch_info_crud.create_branch_info_if_not_exists(db_connection=db_connection, branch_info=branch_info)


@router.get("/{branch_info_id}",
            response_model=branch_info_schema.BranchInfoRead,
            status_code=status.HTTP_200_OK)
def read_branch_info(branch_info_id: int, db_connection: Session = Depends(get_db_connection)):
    db_branch_info = branch_info_crud.get_branch_info(db_connection, branch_info_id=branch_info_id)
    if db_branch_info is None:
        raise HTTPException(status_code=404, detail="BranchInfo not found")
    return db_branch_info


@router.put("/{branch_info_id}",
            response_model=branch_info_schema.BranchInfoRead,
            status_code=status.HTTP_200_OK)
def update_branch_info(
        branch_info_id: int,
        branch_info: branch_info_schema.BranchInfoCreate,
        db_connection: Session = Depends(get_db_connection)
):
    db_branch_info = branch_info_crud.get_branch_info(db_connection, branch_info_id=branch_info_id)
    if db_branch_info is None:
        raise HTTPException(status_code=404, detail="BranchInfo not found")
    return branch_info_crud.update_branch_info(
        db_connection=db_connection,
        branch_info_id=branch_info_id,
        branch_info=branch_info
    )


@router.delete("/{branch_info_id}",
               status_code=status.HTTP_200_OK)
def delete_branch_info(branch_info_id: int, db_connection: Session = Depends(get_db_connection)):
    db_branch_info = branch_info_crud.get_branch_info(db_connection, branch_info_id=branch_info_id)
    if db_branch_info is None:
        raise HTTPException(status_code=404, detail="BranchInfo not found")
    return branch_info_crud.delete_branch_info(db_connection, branch_info_id)


@router.get("/{branch_info_id}"f"{RWS_ROUTE_SCANS}",
            response_model=PaginationModel[scan_schema.ScanRead],
            status_code=status.HTTP_200_OK)
def get_scans_for_branch(branch_info_id: int, skip: int = Query(default=0, ge=0),
                         limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                         db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[scan_schema.ScanRead]:
    """
        Retrieve all scan objects related to a branch paginated
    :param db_connection:
        Session of the database connection
    :param branch_info_id:
        id of the parent branch_info object of which to retrieve scan objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [ScanRead]
        The output will contain a PaginationModel containing the list of ScanRead type objects,
        or an empty list if no scan was found
    """
    scans = scan_crud.get_scans(db_connection, skip=skip, limit=limit, branch_info_id=branch_info_id)

    total_scans = scan_crud.get_scans_count(db_connection, branch_info_id=branch_info_id)

    return PaginationModel[scan_schema.ScanRead](data=scans, total=total_scans, limit=limit, skip=skip)


@router.get("/{branch_info_id}"f"{RWS_ROUTE_LAST_SCAN}",
            response_model=scan_schema.ScanRead,
            status_code=status.HTTP_200_OK)
def get_last_scan_for_branch(branch_info_id: int, db_connection: Session = Depends(get_db_connection)) \
        -> scan_schema.ScanRead:
    """
        Retrieve latest scan object related to a branch
    :param db_connection:
        Session of the database connection
    :param branch_info_id:
        id of the parent branch_info object of which to retrieve scan object
    :return: ScanRead
        The output will contain a ScanRead type object,
        or empty if no scan was found
    """
    last_scan = scan_crud.get_latest_scan_for_branch(db_connection, branch_info_id=branch_info_id)

    return last_scan


@router.get("/{branch_info_id}"f"{RWS_ROUTE_FINDINGS_METADATA}",
            response_model=FindingCountModel[branch_info_schema.BranchInfoRead],
            status_code=status.HTTP_200_OK)
def get_findings_metadata_for_branch(branch_info_id: int,
                                     db_connection: Session = Depends(get_db_connection)) \
        -> FindingCountModel[branch_info_schema.BranchInfoRead]:
    """
        Retrieve findings metadata for a branch
    :param branch_info_id:
        id of the branch_info object for which findings metadata to be retrieved
    :param db_connection:
        Session of the database connection
    :return: BranchedInfoRead, findings count per status
        The output will contain a BranchedInfoRead type object along with findings count per status,
        or empty if no scan was found
    """
    branch_info = branch_info_crud.get_branch_info(db_connection, branch_info_id=branch_info_id)
    if branch_info is None:
        raise HTTPException(status_code=404, detail="BranchInfo not found")

    findings_meta_data = branch_info_crud.get_findings_metadata_by_branch_info_id(db_connection,
                                                                                  branch_info_id=branch_info_id)

    return FindingCountModel[branch_info_schema.BranchInfoRead](
        data=branch_info,
        true_positive=findings_meta_data["true_positive"],
        false_positive=findings_meta_data["false_positive"],
        not_analyzed=findings_meta_data["not_analyzed"],
        under_review=findings_meta_data["under_review"],
        clarification_required=findings_meta_data["clarification_required"],
        total_findings_count=findings_meta_data["total_findings_count"])
