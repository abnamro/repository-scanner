# Standard Library
import logging
from datetime import datetime, timedelta
from typing import Optional

# Third Party
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_cache.decorator import cache

# First Party
from resc_backend.constants import (
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    METRICS_TAG,
    REDIS_CACHE_EXPIRE,
    RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME,
    RWS_ROUTE_AUDITED_COUNT_OVER_TIME,
    RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK,
    RWS_ROUTE_METRICS,
    RWS_ROUTE_PERSONAL_AUDITS,
    RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import audit as audit_crud
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema.audit_count_over_time import AuditCountOverTime
from resc_backend.resc_web_service.schema.finding_count_over_time import FindingCountOverTime
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.personal_audit_metrics import PersonalAuditMetrics
from resc_backend.resc_web_service.schema.time_period import TimePeriod
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
@cache(expire=REDIS_CACHE_EXPIRE)
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
@cache(expire=REDIS_CACHE_EXPIRE)
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
@cache(expire=REDIS_CACHE_EXPIRE)
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


@router.get(f"{RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME}",
            response_model=list[AuditCountOverTime],
            summary="Get count of Audits by Auditor over time for given weeks",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve count of Audits by Auditor over time for given weeks"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
@cache(expire=REDIS_CACHE_EXPIRE)
def get_audit_count_by_auditor_over_time(db_connection: Session = Depends(get_db_connection),
                                         weeks: Optional[int] = Query(default=13, ge=1)) \
        -> list[AuditCountOverTime]:
    """
        Retrieve count of Audits by Auditor over time for given weeks
    - **db_connection**: Session of the database connection
    - **weeks**: Nr of weeks for which to retrieve the audit counts
    - **return**: [AuditCountOverTime]
        The output will contain a list of AuditCountOverTime type objects
    """
    audit_counts = audit_crud.get_audit_count_by_auditor_over_time(db_connection=db_connection, weeks=weeks)

    # get the unique auditors from the data
    auditors_default = {}
    for audit in audit_counts:
        auditors_default[audit['auditor']] = 0

    # default to 0 per auditor for all weeks in range
    weekly_audit_counts = {}
    for week in range(0, weeks):
        nth_week = datetime.utcnow() - timedelta(weeks=week)
        week = f"{nth_week.isocalendar().year} W{nth_week.isocalendar().week:02d}"
        weekly_audit_counts[week] = AuditCountOverTime(time_period=week, audit_by_auditor_count=dict(auditors_default))
    weekly_audit_counts = dict(sorted(weekly_audit_counts.items()))

    # set the counts based on the data from the database
    for audit in audit_counts:
        audit_week = f"{audit['year']} W{audit['week']:02d}"
        weekly_audit_counts.get(audit_week).audit_by_auditor_count[audit['auditor']] = audit['audit_count']
        weekly_audit_counts.get(audit_week).total += audit['audit_count']

    sorted_weekly_audit_counts = dict(sorted(weekly_audit_counts.items()))
    output = list(sorted_weekly_audit_counts.values())
    return output


@router.get(f"{RWS_ROUTE_PERSONAL_AUDITS}",
            response_model=PersonalAuditMetrics,
            summary="Get personal audit metrics",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Get personal audit metrics"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_personal_audit_metrics(request: Request, db_connection: Session = Depends(get_db_connection)) \
        -> PersonalAuditMetrics:
    """
        Retrieve personal audit metrics
    - **db_connection**: Session of the database connection
    - **return**: [DateCountModel]
        The output will contain a PersonalAuditMetrics type objects
    """
    audit_counts = PersonalAuditMetrics()
    audit_counts.today = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                             auditor=request.user, time_period=TimePeriod.DAY)
    audit_counts.current_week = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                                    auditor=request.user, time_period=TimePeriod.WEEK)
    audit_counts.last_week = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                                 auditor=request.user, time_period=TimePeriod.LAST_WEEK)
    audit_counts.current_month = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                                     auditor=request.user, time_period=TimePeriod.MONTH)
    audit_counts.current_year = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                                    auditor=request.user, time_period=TimePeriod.YEAR)
    audit_counts.forever = audit_crud.get_personal_audit_count(db_connection=db_connection,
                                                               auditor=request.user, time_period=TimePeriod.FOREVER)

    audit_counts.rank_current_week = determine_audit_rank_current_week(auditor=request.user,
                                                                       db_connection=db_connection)
    return audit_counts


def determine_audit_rank_current_week(auditor: str, db_connection: Session) -> int:
    """
        Retrieve personal audit ranking this week, compared to other auditors
    - **db_connection**: Session of the database connection
    - **auditor**: id of the auditor
    - **return**: int
        The output will be an integer nr of the ranking this week, defaulting to 0 if no audit was done by the auditor
    """
    audit_rank = 0
    audit_counts_db = audit_crud.get_audit_count_by_auditor_over_time(db_connection=db_connection, weeks=1)

    auditor_counts = {}
    for audit in audit_counts_db:
        auditor_counts[audit['auditor']] = audit['audit_count']

    sorted_auditor_counts = sorted(auditor_counts.items(), key=lambda x: x[1], reverse=True)
    for auditor_count in dict(sorted_auditor_counts):
        audit_rank += 1
        if auditor_count == auditor:
            return audit_rank
    return 0
