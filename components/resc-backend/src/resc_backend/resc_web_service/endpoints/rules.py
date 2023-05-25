# Standard Library
import logging
from datetime import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, Query, status

# First Party
from resc_backend.constants import (
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    RULES_TAG,
    RWS_ROUTE_DETECTED_RULES,
    RWS_ROUTE_FINDING_STATUS_COUNT,
    RWS_ROUTE_RULES
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.rule_count_model import RuleFindingCountModel
from resc_backend.resc_web_service.schema.status_count import StatusCount
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(tags=[RULES_TAG])

logger = logging.getLogger(__name__)


@router.get(f"{RWS_ROUTE_DETECTED_RULES}",
            response_model=List[str],
            summary="Get unique rules from findings",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the unique detected rules across all the findings"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_distinct_rules_from_findings(
        finding_statuses: List[FindingStatus] = Query(None, alias="findingstatus", title="FindingStatuses"),
        vcs_providers: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
        project_name: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
        repository_name: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
        start_date_time: Optional[datetime] = Query(None),
        end_date_time: Optional[datetime] = Query(None),
        rule_pack_versions: Optional[List[str]] = Query(None, alias="rule_pack_version", title="RulePackVersion"),
        db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all uniquely detected rules across all findings in the database

    - **db_connection**: Session of the database connection
    - **finding_statuses**: Optional, filter on supported finding statuses
    - **vcs_providers**: Optional, filter on supported vcs provider types
    - **project_name**: Optional, filter on project name. It is used as a full string match filter
    - **repository_name**: Optional, filter on repository name. It is used as a string contains filter
    - **start_date_time**: Optional, filter on start date
    - **end_date_time**: Optional, filter on end date
    - **rule_pack_version**: Optional, filter on rule pack version
    - **return**: List[str] The output will contain a list of strings of unique rules in the findings table
    """
    distinct_rules = finding_crud.get_distinct_rules_from_findings(db_connection,
                                                                   finding_statuses=finding_statuses,
                                                                   vcs_providers=vcs_providers,
                                                                   project_name=project_name,
                                                                   repository_name=repository_name,
                                                                   start_date_time=start_date_time,
                                                                   end_date_time=end_date_time,
                                                                   rule_pack_versions=rule_pack_versions)
    rules = [rule.rule_name for rule in distinct_rules]
    return rules


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}",
            response_model=List[RuleFindingCountModel],
            summary="Get detected rules with counts per status",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the detected rules with counts per status"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_rules_finding_status_count(
        rule_pack_versions: Optional[List[str]] = Query(None, alias="rule_pack_version", title="RulePackVersion"),
        rule_tags: Optional[List[str]] = Query(None, alias="rule_tag", title="RuleTag"),
        db_connection: Session = Depends(get_db_connection)) -> List[RuleFindingCountModel]:
    """
        Retrieve all detected rules with finding counts per supported status

    - **rule_pack_version**: Optional, filter on rule pack version
    - **rule_tag**: Optional, filter on rule tag
    - **db_connection**: Session of the database connection
    - **return**: List[str] The output will contain a list of strings of unique rules with counts per status
    """
    rule_finding_counts = finding_crud.get_rule_findings_count_by_status(db_connection,
                                                                         rule_pack_versions=rule_pack_versions,
                                                                         rule_tags=rule_tags)
    rule_findings_counts = []

    for rule_name, rule_counts in rule_finding_counts.items():
        rule_finding_count = RuleFindingCountModel(rule_name=rule_name,
                                                   finding_count=rule_counts["total_findings_count"])
        rule_finding_count.finding_statuses_count.append(
            StatusCount(status=FindingStatus.TRUE_POSITIVE, count=rule_counts["true_positive"]))
        rule_finding_count.finding_statuses_count.append(
            StatusCount(status=FindingStatus.FALSE_POSITIVE, count=rule_counts["false_positive"]))
        rule_finding_count.finding_statuses_count.append(
            StatusCount(status=FindingStatus.NOT_ANALYZED, count=rule_counts["not_analyzed"]))
        rule_finding_count.finding_statuses_count.append(
            StatusCount(status=FindingStatus.UNDER_REVIEW, count=rule_counts["under_review"]))
        rule_finding_count.finding_statuses_count.append(
            StatusCount(status=FindingStatus.CLARIFICATION_REQUIRED, count=rule_counts["clarification_required"]))
        rule_findings_counts.append(rule_finding_count)

    return rule_findings_counts
