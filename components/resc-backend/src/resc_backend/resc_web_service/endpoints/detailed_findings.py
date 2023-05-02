# Standard Library
import json
import logging
import urllib.parse

# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# First Party
from resc_backend.constants import (
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    ERROR_MESSAGE_500,
    ERROR_MESSAGE_503,
    FINDINGS_TAG,
    RWS_ROUTE_DETAILED_FINDINGS
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import detailed_finding as detailed_finding_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.helpers.resc_swagger_models import Model404
from resc_backend.resc_web_service.schema import detailed_finding as detailed_finding_schema
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel

router = APIRouter(prefix=f"{RWS_ROUTE_DETAILED_FINDINGS}", tags=[FINDINGS_TAG])
logger = logging.getLogger(__name__)


@router.get("",
            response_model=PaginationModel[detailed_finding_schema.DetailedFindingRead],
            summary="Get all detailed findings",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve all the findings"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def get_all_detailed_findings(skip: int = Query(default=0, ge=0),
                              limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                              db_connection: Session = Depends(get_db_connection),
                              query_string: str = None
                              ) \
        -> PaginationModel[detailed_finding_schema.DetailedFindingRead]:
    """
        Retrieve all findings objects paginated
    - **query_string**

        A query string with the following format:
            param1=value1&param2=value2&param3=value3

        Where the possible parameters are:

            - vcs_providers [enum] of type VCSProviders, possible values are: BITBUCKET, AZURE_DEVOPS.
                Will default to all if non-specified.

            - finding_statuses [enum of type FindingStatus], possible values are:NOT_ANALYZED,FALSE_POSITIVE,
              TRUE_POSITIVE. Will default to all if non-specified.

            - rule_pack_versions of type [String]

            - rule_names of type [String]

            - rule_tags of type [String] findings in the result will have at least one of the specified tags
              for the rules

            - project_name of type String

            - repository_names of type [String]

            - branch_name of type String

            - scan_ids of type list Integer

            - start_date_time of type datetime with the following format: 1970-01-31T00:00:00

            - end_date_time of type datetime with the following format: 1970-01-31T00:00:00

    - **db_connection**

        Session of the database connection

    - **skip**

        Integer amount of records to skip to support pagination

    - **limit**

        Integer amount of records to return, to support pagination

    - **return** [FindingRead]

        The output will contain a PaginationModel containing the list of DetailedFinding type objects,
        or an empty list if no finding was found
    """

    parsed_query_string_params = dict(urllib.parse.parse_qsl(query_string))

    if parsed_query_string_params.get('scan_ids'):
        parsed_query_string_params['scan_ids'] = json.loads(parsed_query_string_params['scan_ids'])
    if parsed_query_string_params.get('vcs_providers'):
        parsed_query_string_params['vcs_providers'] = json.loads(parsed_query_string_params['vcs_providers']
                                                                 .replace('\'', '"'))
    if parsed_query_string_params.get('finding_statuses'):
        parsed_query_string_params['finding_statuses'] = json.loads(parsed_query_string_params['finding_statuses']
                                                                    .replace('\'', '"'))
    if parsed_query_string_params.get('rule_names'):
        parsed_query_string_params['rule_names'] = json.loads(parsed_query_string_params['rule_names']
                                                              .replace('\'', '"'))
    if parsed_query_string_params.get('rule_tags'):
        parsed_query_string_params['rule_tags'] = json.loads(parsed_query_string_params['rule_tags']
                                                             .replace('\'', '"'))
    if parsed_query_string_params.get('rule_pack_versions'):
        parsed_query_string_params['rule_pack_versions'] = json.loads(parsed_query_string_params['rule_pack_versions']
                                                                      .replace('\'', '"'))

    findings_filter = FindingsFilter(**parsed_query_string_params)

    findings = detailed_finding_crud.get_detailed_findings(
        db_connection, findings_filter=findings_filter, skip=skip, limit=limit)
    total_findings = detailed_finding_crud.get_detailed_findings_count(
        db_connection, findings_filter=findings_filter)

    return PaginationModel[detailed_finding_schema.DetailedFindingRead](
        data=findings, total=total_findings, limit=limit, skip=skip)


@router.get("/{finding_id}",
            response_model=detailed_finding_schema.DetailedFindingRead,
            summary="Fetch detailed finding by ID",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Retrieve detailed finding <finding_id>"},
                404: {"model": Model404, "description": "Finding <finding_id> not found"},
                500: {"description": ERROR_MESSAGE_500},
                503: {"description": ERROR_MESSAGE_503}
            })
def read_finding(finding_id: int, db_connection: Session = Depends(get_db_connection)) \
        -> detailed_finding_schema.DetailedFindingRead:
    """
        Retrieve detailed finding by its ID

    - **db_connection**: Session of the database connection
    - **finding_id**: ID of the finding for which details need to be fetched
    - **return**: [DetailedFindingRead]
        The output will contain the details of a finding
    """
    db_finding = detailed_finding_crud.get_detailed_finding(db_connection, finding_id=finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db_finding
