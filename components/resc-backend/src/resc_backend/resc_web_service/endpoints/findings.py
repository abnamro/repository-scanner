# Standard Library
from datetime import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

# First Party
from resc_backend.constants import (
    CACHE_MAX_AGE,
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    FINDINGS_TAG,
    RWS_ROUTE_AUDIT,
    RWS_ROUTE_BY_RULE,
    RWS_ROUTE_COUNT_BY_TIME,
    RWS_ROUTE_FINDINGS,
    RWS_ROUTE_SUPPORTED_STATUSES,
    RWS_ROUTE_TOTAL_COUNT_BY_RULE
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import scan_finding as scan_finding_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema import audit as audit_schema
from resc_backend.resc_web_service.schema import finding as finding_schema
from resc_backend.resc_web_service.schema.date_count_model import DateCountModel
from resc_backend.resc_web_service.schema.date_filter import DateFilter
from resc_backend.resc_web_service.schema.finding import FindingRead
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel

router = APIRouter(prefix=f"{RWS_ROUTE_FINDINGS}", tags=[FINDINGS_TAG])


@router.get("",
            response_model=PaginationModel[finding_schema.FindingRead],
            status_code=status.HTTP_200_OK)
def get_all_findings(skip: int = Query(default=0, ge=0),
                     limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                     db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[finding_schema.FindingRead]:
    """
        Retrieve all findings objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [FindingRead]
        The output will contain a PaginationModel containing the list of FindingRead type objects,
        or an empty list if no finding was found
    """
    findings = finding_crud.get_findings(db_connection, skip=skip, limit=limit)

    total_findings = finding_crud.get_total_findings_count(db_connection)

    return PaginationModel[finding_schema.FindingRead](data=findings, total=total_findings, limit=limit, skip=skip)


@router.post("",
             response_model=int,
             status_code=status.HTTP_201_CREATED)
def create_findings(findings: List[finding_schema.FindingCreate], db_connection: Session = Depends(get_db_connection)) \
        -> int:
    """
          Create new findings
      :param db_connection:
          Session of the database connection
      :param findings:
          List of findings to create
      :return: int
          The output will contain the number of successful created findings
      """
    try:
        created_findings = finding_crud.create_findings(db_connection=db_connection, findings=findings)

    except KeyError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return len(created_findings)


@router.get("/{finding_id}",
            response_model=finding_schema.FindingRead,
            status_code=status.HTTP_200_OK)
def read_finding(finding_id: int, db_connection: Session = Depends(get_db_connection)):
    db_finding = finding_crud.get_finding(db_connection, finding_id=finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    db_scan_findings = scan_finding_crud.get_scan_findings(db_connection, finding_id=finding_id)
    scan_ids = [x.scan_id for x in db_scan_findings]
    return FindingRead.create_from_db_entities(db_finding=db_finding, scan_ids=scan_ids)


@router.patch("/{finding_id}",
              response_model=finding_schema.FindingRead,
              status_code=status.HTTP_200_OK)
def patch_finding(
        finding_id: int,
        finding_update: finding_schema.FindingPatch,
        db_connection: Session = Depends(get_db_connection)
):
    db_finding = finding_crud.get_finding(db_connection, finding_id=finding_id)
    db_sca_findings = scan_finding_crud.get_scan_findings(db_connection, finding_id=finding_id)
    scan_ids = [x.scan_id for x in db_sca_findings]
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingRead.create_from_db_entities(
        finding_crud.patch_finding(db_connection, finding_id=finding_id, finding_update=finding_update),
        scan_ids
    )


@router.put("/{finding_id}",
            response_model=finding_schema.FindingRead,
            status_code=status.HTTP_200_OK)
def update_finding(
        finding_id: int,
        finding: finding_schema.FindingUpdate,
        db_connection: Session = Depends(get_db_connection)
):
    db_finding = finding_crud.get_finding(db_connection, finding_id=finding_id)
    db_sca_findings = scan_finding_crud.get_scan_findings(db_connection, finding_id=finding_id)
    scan_ids = [x.scan_id for x in db_sca_findings]
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingRead.create_from_db_entities(
        finding_crud.update_finding(db_connection=db_connection, finding_id=finding_id, finding=finding),
        scan_ids
    )


@router.delete("/{finding_id}",
               status_code=status.HTTP_200_OK)
def delete_finding(finding_id: int, db_connection: Session = Depends(get_db_connection)) -> FindingRead:
    """
        Delete a finding object
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to delete
    :return:
        The output will contain a success or error message based on the success of the deletion
    """
    db_finding = finding_crud.get_finding(db_connection, finding_id=finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding_crud.delete_finding(db_connection, finding_id=finding_id, delete_related=True)
    return {"ok": True}


@router.get(f"{RWS_ROUTE_TOTAL_COUNT_BY_RULE}""/{rule_name}",
            status_code=status.HTTP_200_OK)
def get_total_findings_count_by_rule(rule_name: str, db_connection: Session = Depends(get_db_connection)):
    findings_filter = FindingsFilter(rule_names=[rule_name])
    return finding_crud.get_total_findings_count(db_connection, findings_filter=findings_filter)


@router.get(f"{RWS_ROUTE_BY_RULE}""/{rule_name}",
            response_model=PaginationModel[finding_schema.FindingRead],
            status_code=status.HTTP_200_OK)
def get_findings_by_rule(rule_name: str, skip: int = Query(default=0, ge=0),
                         limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                         db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[finding_schema.FindingRead]:
    """
        Retrieve all findings objects paginated by rule
    :param db_connection:
        Session of the database connection
    :param rule_name:
        Name of the rule to filter the findings by
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [FindingRead]
        The output will contain a PaginationModel containing the list of FindingRead type objects,
        or an empty list if no finding was found for the given rule
    """
    findings = finding_crud.get_findings_by_rule(db_connection, skip=skip, limit=limit, rule_name=rule_name)
    total_findings = finding_crud.get_total_findings_count(
        db_connection, findings_filter=FindingsFilter(rule_names=[rule_name]))
    return PaginationModel[finding_schema.FindingRead](data=findings, total=total_findings, limit=limit, skip=skip)


@router.put(f"{RWS_ROUTE_AUDIT}/",
            response_model=List[finding_schema.FindingRead],
            status_code=status.HTTP_200_OK)
def audit_findings(
        audit: audit_schema.AuditMultiple,
        db_connection: Session = Depends(get_db_connection)
) -> List[finding_schema.FindingRead]:
    """
        Audit single/multiple findings, updating the status and comment
    :param db_connection:
        Session of the database connection
    :param audit:
        audit object, containing the ids to audit, status to set and the comment
    :return: [FindingRead]
        The output will contain a list of the findings that where updated
    """
    audited_findings = []
    for finding_id in audit.finding_ids:
        db_finding = finding_crud.get_finding(db_connection, finding_id=finding_id)
        db_scan_findings = scan_finding_crud.get_scan_findings(db_connection, finding_id=finding_id)
        scan_ids = [x.scan_id for x in db_scan_findings]
        if db_finding is None:
            raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found")

        audited_findings.append(
            FindingRead.create_from_db_entities(
                finding_crud.audit_finding(db_connection=db_connection, db_finding=db_finding,
                                           status=audit.status, comment=audit.comment),
                scan_ids=scan_ids)
        )
    return audited_findings


@router.get(f"{RWS_ROUTE_SUPPORTED_STATUSES}/",
            response_model=List[str],
            status_code=status.HTTP_200_OK)
def get_supported_statuses(response: Response) -> List[str]:
    """
        Retrieve all supported statuses for findings
    :return: List[str]
        The output will contain a list of strings of unique statuses supported
    """
    response.headers["Cache-Control"] = CACHE_MAX_AGE
    supported_finding_statuses = [finding_status for finding_status in FindingStatus if finding_status]
    return supported_finding_statuses


@router.get(f"{RWS_ROUTE_COUNT_BY_TIME}/""{time_type}",
            response_model=PaginationModel[DateCountModel],
            status_code=status.HTTP_200_OK)
def get_count_by_time(time_type: DateFilter,
                      skip: int = Query(default=0, ge=0),
                      limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                      start_date_time: Optional[datetime] = Query(None),
                      end_date_time: Optional[datetime] = Query(None),
                      db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[DateCountModel]:
    """
        Retrieve all findings count by time period objects paginated
    :param db_connection:
        Session of the database connection
    :param time_type:
        required, filter on time_type
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param start_date_time
        Optional, filter on start date
    :param end_date_time
        Optional, filter on end date
    :return: PaginationModel[DateCountModel]
        The output will contain a PaginationModel containing the list of DateCountModel type objects,
        or an empty list if no data was found
    """
    date_counts = []
    findings = finding_crud.get_findings_count_by_time(db_connection=db_connection, date_type=time_type,
                                                       start_date_time=start_date_time, end_date_time=end_date_time,
                                                       skip=skip, limit=limit)
    total_findings = finding_crud.get_findings_count_by_time_total(db_connection=db_connection, date_type=time_type,
                                                                   start_date_time=start_date_time,
                                                                   end_date_time=end_date_time)
    for finding in findings:
        if time_type == DateFilter.MONTH:
            date_count = DateCountModel(finding_count=finding[2], date_lable=f"{finding[0]}-{finding[1]}")
        elif time_type == DateFilter.WEEK:
            date_count = DateCountModel(finding_count=finding[2], date_lable=f"{finding[0]}-W{finding[1]}")
        elif time_type == DateFilter.DAY:
            date_count = DateCountModel(finding_count=finding[3], date_lable=f"{finding[0]}-{finding[1]}-{finding[2]}")

        date_counts.append(date_count)

    return PaginationModel[DateCountModel](data=date_counts, total=total_findings, limit=limit, skip=skip)
