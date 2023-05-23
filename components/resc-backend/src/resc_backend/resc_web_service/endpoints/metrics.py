# Standard Library
import logging
from datetime import datetime, timedelta
from typing import Optional

# Third Party
from fastapi import APIRouter, Depends, Query, status

# First Party
from resc_backend.constants import (
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    METRICS_TAG,
    RWS_ROUTE_AUDITED_COUNT_OVER_TIME,
    RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK,
    RWS_ROUTE_METRICS,
    RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema.finding_count_over_time import FindingCountOverTime
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(prefix=f"{RWS_ROUTE_METRICS}", tags=[METRICS_TAG])
logger = logging.getLogger(__name__)


@router.get(f"{RWS_ROUTE_AUDITED_COUNT_OVER_TIME}",
            response_model=list[FindingCountOverTime],
            summary="Get count of audit status over time for given weeks per vcs provider",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve count of audit status over time for given weeks per vcs provider"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_finding_audit_count_over_time(db_connection: Session = Depends(get_db_connection),
                                      weeks: Optional[int] = Query(default=13, ge=1),
                                      audit_status: Optional[FindingStatus] = Query(default=FindingStatus.TRUE_POSITIVE)
                                      ) -> list[FindingCountOverTime]:
    """
        Retrieve count of audited findings over time for given weeks per vcs provider
    - **db_connection**: Session of the database connection
    - **weeks**: Nr of weeks for which to retrieve the audit status count
    - **audit_status**: audit status for which to retrieve the counts, defaults to True positive
    - **return**: [DateCountModel]
        The output will contain a list of DateCountModel type objects
    """
    audit_counts = finding_crud.get_finding_audit_status_count_over_time(db_connection=db_connection,
                                                                         status=audit_status,
                                                                         weeks=weeks)
    output = convert_rows_to_finding_count_over_time(count_over_time=audit_counts, weeks=weeks)
    return output


@router.get(f"{RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK}",
            response_model=list[FindingCountOverTime],
            summary="Get count of findings over time for given weeks per vcs provider",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve count of findings over time for given weeks per vcs provider"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_finding_total_count_over_time(db_connection: Session = Depends(get_db_connection),
                                      weeks: Optional[int] = Query(default=13, ge=1)) -> list[FindingCountOverTime]:
    """
        Retrieve count of findings over time for given weeks per vcs provider
    - **db_connection**: Session of the database connection
    - **weeks**: Nr of weeks for which to retrieve the audit status count
    - **audit_status**: audit status for which to retrieve the counts, defaults to True positive
    - **return**: [DateCountModel]
        The output will contain a list of DateCountModel type objects
    """
    audit_counts = finding_crud.get_finding_count_by_vcs_provider_over_time(db_connection=db_connection, weeks=weeks)
    output = convert_rows_to_finding_count_over_time(count_over_time=audit_counts, weeks=weeks)
    return output


@router.get(f"{RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME}",
            response_model=list[FindingCountOverTime],
            summary="Get count of UnTriaged findings over time for given weeks per vcs provider",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve count of UnTriaged findings over time for given weeks per vcs provider"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_finding_un_triaged_count_over_time(db_connection: Session = Depends(get_db_connection),
                                           weeks: Optional[int] = Query(default=13, ge=1)) \
        -> list[FindingCountOverTime]:
    """
        Retrieve count of UnTriaged findings over time for given weeks per vcs provider
    - **db_connection**: Session of the database connection
    - **weeks**: Nr of weeks for which to retrieve the audit status count
    - **audit_status**: audit status for which to retrieve the counts, defaults to True positive
    - **return**: [DateCountModel]
        The output will contain a list of DateCountModel type objects
    """
    audit_counts = finding_crud.get_un_triaged_finding_count_by_vcs_provider_over_time(db_connection=db_connection,
                                                                                       weeks=weeks)
    output = convert_rows_to_finding_count_over_time(count_over_time=audit_counts, weeks=weeks)
    return output


def convert_rows_to_finding_count_over_time(count_over_time: dict, weeks: int) -> list[FindingCountOverTime]:
    """
        Convert the rows from the database to the format of list[FindingCountOverTime]
    :param count_over_time:
        rows from the database
    :param weeks:
        number fo weeks that are in the data
    :return: output
        list[FindingCountOverTime]
    """
    # Define the vcs provider types and finding statuses
    vcs_provider_types = list(VCSProviders)

    # create defaults with 0 value
    week_groups = {}
    for week in range(0, weeks):
        nth_week = datetime.utcnow() - timedelta(weeks=week)
        week = f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"
        week_groups[week] = {vcs_provider_type: 0 for vcs_provider_type in vcs_provider_types + ["total"]}

    # loop over the counts from the database
    for data in count_over_time:
        week = f"{data['year']} W{data['week']:02d}"
        finding_count = data["finding_count"]

        week_groups[week][data["provider_type"]] += finding_count
        week_groups[week]["total"] += finding_count

    # Convert to the output format
    output = []
    for week in sorted(week_groups.keys()):
        week_data = FindingCountOverTime(time_period=week, total=week_groups[week]["total"])
        for vcs_provider_type in vcs_provider_types:
            setattr(week_data.vcs_provider_finding_count, vcs_provider_type, week_groups[week][vcs_provider_type])

        output.append(week_data)
    return output
