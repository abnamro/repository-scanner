# Standard Library
import logging
from datetime import datetime
from typing import List, Optional

# Third Party
from fastapi import APIRouter, Depends, Query, status

# First Party
from resc_backend.constants import RULES_TAG, RWS_ROUTE_DETECTED_RULES, RWS_ROUTE_FINDING_STATUS_COUNT, RWS_ROUTE_RULES
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import rule as rule_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.rule import RuleCreate
from resc_backend.resc_web_service.schema.rule_count_model import RuleFindingCountModel
from resc_backend.resc_web_service.schema.status_count import StatusCount
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(tags=[RULES_TAG])

logger = logging.getLogger(__name__)


@router.get(f"{RWS_ROUTE_DETECTED_RULES}",
            response_model=List[str],
            status_code=status.HTTP_200_OK)
def get_distinct_rules_from_findings(
        finding_statuses: List[FindingStatus] = Query(None, alias="findingstatus", title="FindingStatuses"),
        vcs_providers: List[VCSProviders] = Query(None, alias="vcsprovider", title="VCSProviders"),
        project_name: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
        repository_name: Optional[str] = Query('', regex=r"^[A-z0-9 .\-_%]*$"),
        start_date_time: Optional[datetime] = Query(None),
        end_date_time: Optional[datetime] = Query(None),
        db_connection: Session = Depends(get_db_connection)) -> List[str]:
    """
        Retrieve all uniquely detected rules across all findings in the database
    :param finding_statuses:
        optional, filter of supported finding statuses
    :param vcs_providers:
        optional, filter of supported vcs provider types
    :param db_connection:
        Session of the database connection
    :param project_name:
        optional, filter on project name. Is used as a full string match filter
    :param repository_name:
        Optional, filter on repository name. Is used as a string contains filter
    :param start_date_time
        Optional, filter on start date
    :param end_date_time
        Optional, filter on end date
    :return: List[str]
        The output will contain a list of strings of unique rules in the findings table
    """
    distinct_rules = finding_crud.get_distinct_rules_from_findings(db_connection,
                                                                   finding_statuses=finding_statuses,
                                                                   vcs_providers=vcs_providers,
                                                                   project_name=project_name,
                                                                   repository_name=repository_name,
                                                                   start_date_time=start_date_time,
                                                                   end_date_time=end_date_time)
    rules = [rule.rule_name for rule in distinct_rules]
    return rules


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}",
            response_model=List[RuleFindingCountModel],
            status_code=status.HTTP_200_OK)
def get_rules_finding_status_count(db_connection: Session = Depends(get_db_connection)) -> List[RuleFindingCountModel]:
    """
        Retrieve all detected rules with finding counts per supported status
    :param db_connection:
        Session of the database connection
    :return: List[str]
        The output will contain a list of strings of unique rules in the findings table
    """
    distinct_rules = finding_crud.get_distinct_rules_from_findings(db_connection)

    rule_findings_counts = []
    for rule in distinct_rules:
        finding_count = 0
        rule_finding_count = RuleFindingCountModel(rule_name=rule.rule_name)
        count_by_status = finding_crud.get_findings_count_by_status(db_connection,
                                                                    rule_name=rule_finding_count.rule_name)
        handled_statuses = []
        for status_count in count_by_status:
            finding_status_count = StatusCount(status=status_count[0], count=status_count[1])
            finding_count = finding_count + finding_status_count.count
            handled_statuses.append(finding_status_count.status)
            rule_finding_count.finding_statuses_count.append(finding_status_count)

        for finding_status in FindingStatus:
            # add default values of 0 for statuses without findings
            if finding_status not in handled_statuses:
                finding_status_count = StatusCount(status=finding_status, count=0)
                rule_finding_count.finding_statuses_count.append(finding_status_count)

        rule_finding_count.finding_count = finding_count
        rule_finding_count.finding_statuses_count = sorted(rule_finding_count.finding_statuses_count,
                                                           key=lambda status_counter: status_counter.status)
        rule_findings_counts.append(rule_finding_count)

    return rule_findings_counts


def create_rule(
        rule: RuleCreate,
        db_connection: Session = Depends(get_db_connection)):
    """
        Create rule in database
    :param rule:
        RuleCreate object to be created
    :param db_connection:
        Session of the database connection
    """
    return rule_crud.create_rule(db_connection=db_connection,
                                 rule=rule)
