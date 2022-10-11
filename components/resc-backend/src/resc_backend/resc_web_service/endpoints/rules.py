# Standard Library
import logging
from datetime import datetime
from typing import List, Optional

# Third Party
import tomlkit
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from packaging.version import Version

# First Party
from resc_backend.constants import (
    DEFAULT_RECORDS_PER_PAGE_LIMIT,
    RULES_TAG,
    RWS_ROUTE_DETECTED_RULES,
    RWS_ROUTE_DOWNLOAD_RULE_PACK,
    RWS_ROUTE_FINDING_STATUS_COUNT,
    RWS_ROUTE_RULE_ALLOW_LIST,
    RWS_ROUTE_RULE_PACK,
    RWS_ROUTE_RULE_PACKS,
    RWS_ROUTE_RULES,
    RWS_ROUTE_UPLOAD_RULE_PACK
)
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import rule as rule_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.helpers.rule import (
    create_toml_dictionary,
    create_toml_rule_file,
    get_mapped_global_allow_list_obj,
    map_dictionary_to_rule_allow_list_object,
    validate_uploaded_file_and_read_content
)
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel
from resc_backend.resc_web_service.schema.rule import RuleCreate, RuleRead
from resc_backend.resc_web_service.schema.rule_allow_list import RuleAllowList, RuleAllowListRead
from resc_backend.resc_web_service.schema.rule_count_model import RuleFindingCountModel
from resc_backend.resc_web_service.schema.rule_pack import RulePackCreate, RulePackRead
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
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
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
    :param start_date
        Optional, filter on start date
    :param end_date
        Optional, filter on end date
    :return: List[str]
        The output will contain a list of strings of unique rules in the findings table
    """
    distinct_rules = finding_crud.get_distinct_rules_from_findings(db_connection,
                                                                   finding_statuses=finding_statuses,
                                                                   vcs_providers=vcs_providers,
                                                                   project_name=project_name,
                                                                   repository_name=repository_name,
                                                                   start_date=start_date,
                                                                   end_date=end_date)
    rules = [rule.rule_name for rule in distinct_rules]
    return rules


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_FINDING_STATUS_COUNT}",
            response_model=List[RuleFindingCountModel],
            status_code=status.HTTP_200_OK)
def get_rules_finding_status_count(db_connection: Session = Depends(get_db_connection)) -> List[RuleFindingCountModel]:
    """
        Retrieve all detected rules with finding counts per supported status
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


@router.post(f"{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_ALLOW_LIST}",
             response_model=RuleAllowListRead,
             status_code=status.HTTP_201_CREATED)
def create_rule_allow_list(
        rule_allow_list: RuleAllowList,
        db_connection: Session = Depends(get_db_connection)):
    return rule_crud.create_rule_allow_list(db_connection=db_connection,
                                            rule_allow_list=rule_allow_list)


@router.post(f"{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}",
             response_model=RulePackRead,
             status_code=status.HTTP_201_CREATED)
def create_rule_pack_version(
        rule_pack: RulePackCreate,
        db_connection: Session = Depends(get_db_connection)):
    return rule_crud.create_rule_pack_version(db_connection=db_connection,
                                              rule_pack=rule_pack)


@router.post(f"{RWS_ROUTE_RULES}",
             response_model=RuleRead,
             status_code=status.HTTP_201_CREATED)
def create_rule(
        rule: RuleCreate,
        db_connection: Session = Depends(get_db_connection)):
    return rule_crud.create_rule(db_connection=db_connection,
                                 rule=rule)


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACK}",
            response_model=RulePackRead,
            status_code=status.HTTP_200_OK)
def get_rule_pack(version: Optional[str] = Query('', regex=r"^\d+(?:\.\d+){2}$"),
                  db_connection: Session = Depends(get_db_connection)):
    db_rule_pack = rule_crud.get_rule_pack(db_connection=db_connection, version=version)
    return db_rule_pack


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_RULE_PACKS}",
            response_model=PaginationModel[RulePackRead],
            status_code=status.HTTP_200_OK)
def get_all_rule_packs(skip: int = Query(default=0, ge=0),
                       limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                       db_connection: Session = Depends(get_db_connection)):
    rule_packs = rule_crud.get_all_rule_packs(db_connection=db_connection, skip=skip, limit=limit)
    total_rule_packs_count = rule_crud.get_rule_packs_count(db_connection)
    return PaginationModel[RulePackRead](data=rule_packs, total=total_rule_packs_count, limit=limit, skip=skip)


@router.post(f"{RWS_ROUTE_RULES}{RWS_ROUTE_UPLOAD_RULE_PACK}",
             status_code=status.HTTP_200_OK)
def upload_rule_pack_toml_file(rule_file: UploadFile = File(...),
                               db_connection: Session = Depends(get_db_connection)) -> dict:
    content = validate_uploaded_file_and_read_content(rule_file)
    toml_rule_dictionary = tomlkit.loads(content)

    # Check if rule pack version exists
    rule_pack_version = toml_rule_dictionary["version"] if "version" in toml_rule_dictionary else None
    if rule_pack_version is None:
        raise HTTPException(status_code=400, detail="Rule pack version doesn't exist in the TOML file")
    rule_pack_from_db = get_rule_pack(version=rule_pack_version, db_connection=db_connection)
    if rule_pack_from_db:
        raise HTTPException(status_code=409, detail=f"Unable to process rules. Rule pack version "
                                                    f"{rule_pack_version} already exists")
    # Insert in to RULE_ALLOW_LIST for storing global allow list
    created_global_rule_allow_list = None
    global_allow_list: RuleAllowList = get_mapped_global_allow_list_obj(toml_rule_dictionary)
    if global_allow_list:
        created_global_rule_allow_list = create_rule_allow_list(rule_allow_list=global_allow_list,
                                                                db_connection=db_connection)
        if not created_global_rule_allow_list.id_:
            logger.warning("Creating global rule allow list failed with an error")

    # Insert in to RULE_PACK
    global_allow_list_id = created_global_rule_allow_list.id_ if \
        created_global_rule_allow_list and created_global_rule_allow_list.id_ else None

    # Determine if uploaded rule pack needs to be activated
    current_newest_rule_pack = rule_crud.get_newest_rule_pack(db_connection)
    activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(rule_pack_version, current_newest_rule_pack)

    rule_pack = RulePackCreate(version=rule_pack_version, active=activate_uploaded_rule_pack,
                               global_allow_list=global_allow_list_id)
    created_rule_pack_version = create_rule_pack_version(rule_pack=rule_pack, db_connection=db_connection)
    if created_rule_pack_version.version and activate_uploaded_rule_pack:
        # Update older rule packs to inactive
        rule_crud.make_older_rule_packs_to_inactive(latest_rule_pack_version=rule_pack_version,
                                                    db_connection=db_connection)
    else:
        logger.warning("Creating rule pack failed with an error")

    # Insert in to RULES
    if created_rule_pack_version and created_rule_pack_version.version:
        insert_rules(version=rule_pack_version, toml_rule_dictionary=toml_rule_dictionary,
                     db_connection=db_connection)
    return {"filename": rule_file.filename}


@router.get(f"{RWS_ROUTE_RULES}{RWS_ROUTE_DOWNLOAD_RULE_PACK}",
            status_code=status.HTTP_200_OK)
async def download_rule_pack_toml_file(rule_pack_version: Optional[str] = Query(None, regex=r"^\d+(?:\.\d+){2}$"),
                                       db_connection: Session = Depends(get_db_connection)) -> FileResponse:
    if not rule_pack_version:
        logger.info("rule pack version not specified, downloading the currently active version")
    rule_pack_from_db = get_rule_pack(version=rule_pack_version, db_connection=db_connection)
    if rule_pack_from_db:
        version = rule_pack_from_db.version
        rules = rule_crud.get_rules_by_rule_pack_version(db_connection=db_connection,
                                                         rule_pack_version=version)
        global_allow_list = rule_crud.get_global_allow_list_by_rule_pack_version(db_connection=db_connection,
                                                                                 rule_pack_version=version)
        generated_toml_dict = create_toml_dictionary(version, rules, global_allow_list)
    else:
        raise HTTPException(status_code=404, detail="No rulepack found")

    toml_file = create_toml_rule_file(generated_toml_dict)
    return FileResponse(toml_file.name, filename="RESC-SECRETS-RULE.toml")


def insert_rules(version: str, toml_rule_dictionary: dict, db_connection: Session = Depends(get_db_connection)):
    if "rules" in toml_rule_dictionary:
        rule_list = toml_rule_dictionary.get("rules")
        for rule in rule_list:
            tags = None
            keywords = None
            rule_name = rule["id"] if "id" in rule else None
            description = rule["description"] if "description" in rule else None
            regex = rule["regex"] if "regex" in rule else None
            entropy = rule["entropy"] if "entropy" in rule else None
            secret_group = rule["secretGroup"] if "secretGroup" in rule else None
            path = rule["path"] if "path" in rule else None

            if "tags" in rule:
                tag_array = rule["tags"]
                tags = ",".join(tag_array)

            if "keywords" in rule:
                keyword_array = rule["keywords"]
                keywords = ",".join(keyword_array)

            # Insert in to RULE_ALLOW_LIST for storing individual rule specific  allow list
            allow_list = rule["allowlist"] if "allowlist" in rule else None
            rule_allow_list_obj = map_dictionary_to_rule_allow_list_object(allow_list)
            created_rule_allow_list = None
            if rule_allow_list_obj:
                created_rule_allow_list = create_rule_allow_list(rule_allow_list=rule_allow_list_obj,
                                                                 db_connection=db_connection)

            # Insert in to RULES
            if allow_list and created_rule_allow_list and created_rule_allow_list.id_:
                created_allow_list_id = created_rule_allow_list.id_
            else:
                created_allow_list_id = None
            rule_obj = RuleCreate(rule_pack=version,
                                  allow_list=created_allow_list_id,
                                  rule_name=rule_name, description=description, tags=tags, entropy=entropy,
                                  secret_group=secret_group, regex=regex, path=path, keywords=keywords)
            created_rule = create_rule(rule=rule_obj, db_connection=db_connection)
            if not created_rule.id_:
                logger.warning(f"Creating rule failed for Rule: {rule_name}")


def determine_uploaded_rule_pack_activation(requested_rule_pack_version: str, latest_rule_pack_from_db: RulePackRead):
    if latest_rule_pack_from_db:
        if Version(latest_rule_pack_from_db.version) < Version(requested_rule_pack_version):
            logger.info(f"Uploaded rule pack is of version '{requested_rule_pack_version}', using it to replace "
                        f"'{latest_rule_pack_from_db.version}' as the active one.")
            activate_uploaded_rule_pack = True
        else:
            if not latest_rule_pack_from_db.active:
                logger.info(f"There is already a more recent rule pack present in the database "
                            f"'{latest_rule_pack_from_db.version}', but it is set to inactive. "
                            f"Activating the uploaded rule pack '{requested_rule_pack_version}'")
                activate_uploaded_rule_pack = True
            else:
                logger.info(f"Uploaded rule pack is of version '{requested_rule_pack_version}', the existing rule pack "
                            f"'{latest_rule_pack_from_db.version}' is kept as the active one.")
                activate_uploaded_rule_pack = False
    else:
        logger.info(
            f"No existing rule pack found, So activating the uploaded rule pack '{requested_rule_pack_version}'")
        activate_uploaded_rule_pack = True
    return activate_uploaded_rule_pack
