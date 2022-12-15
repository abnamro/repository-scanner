# Standard Library
import logging
import re
from typing import Optional

# Third Party
import tomlkit
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from packaging.version import Version
from pydantic import Required

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, RULE_PACKS_TAG, RWS_ROUTE_RULE_PACKS
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import rule as rule_crud
from resc_backend.resc_web_service.crud import rule_pack as rule_pack_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.helpers.rule import (
    create_toml_dictionary,
    create_toml_rule_file,
    get_mapped_global_allow_list_obj,
    map_dictionary_to_rule_allow_list_object,
    validate_uploaded_file_and_read_content
)
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel
from resc_backend.resc_web_service.schema.rule import RuleCreate
from resc_backend.resc_web_service.schema.rule_allow_list import RuleAllowList
from resc_backend.resc_web_service.schema.rule_pack import RulePackCreate, RulePackRead

router = APIRouter(prefix=f"{RWS_ROUTE_RULE_PACKS}", tags=[RULE_PACKS_TAG])

logger = logging.getLogger(__name__)


@router.get("/versions",
            response_model=PaginationModel[RulePackRead],
            status_code=status.HTTP_200_OK)
def get_rule_packs(version: Optional[str] = Query(None, regex=r"^\d+(?:\.\d+){2}$"),
                   active: Optional[bool] = Query(None, description="Filter on active rule packs"),
                   skip: int = Query(default=0, ge=0),
                   limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                   db_connection: Session = Depends(get_db_connection)) -> PaginationModel[RulePackRead]:
    """
        Retrieve rule packs from database
    :param version:
        optional, filter on rule pack version
    :param active:
        optional, filter on active rule pack
    :param skip:
        integer amount of records to skip, to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param db_connection:
        Session of the database connection
    :return: [RulePackRead]
        The output will contain a PaginationModel containing the list of RulePackRead type objects,
        or an empty list if no rule pack was found
    """
    rule_packs = rule_pack_crud.get_rule_packs(db_connection=db_connection, version=version, active=active, skip=skip,
                                               limit=limit)
    total_rule_packs_count = rule_pack_crud.get_total_rule_packs_count(db_connection=db_connection, version=version,
                                                                       active=active)
    return PaginationModel[RulePackRead](data=rule_packs, total=total_rule_packs_count, limit=limit, skip=skip)


@router.get("", status_code=status.HTTP_200_OK)
async def download_rule_pack_toml_file(version: Optional[str] = Query(None, regex=r"^\d+(?:\.\d+){2}$"),
                                       db_connection: Session = Depends(get_db_connection)) -> FileResponse:
    """
        Download rule pack in TOML format
    :param version:
        optional, filter on rule pack version
    :param db_connection:
        Session of the database connection
    :return: [FileResponse]
        The output returns rule pack file downloaded in TOML format
    """
    if not version:
        logger.info("rule pack version not specified, downloading the currently active version")
    rule_pack_from_db = read_rule_pack(version=version, db_connection=db_connection)
    if rule_pack_from_db:
        version = rule_pack_from_db.version
        rules = rule_crud.get_rules_by_rule_pack_version(db_connection=db_connection,
                                                         rule_pack_version=version)
        global_allow_list = rule_crud.get_global_allow_list_by_rule_pack_version(db_connection=db_connection,
                                                                                 rule_pack_version=version)
        generated_toml_dict = create_toml_dictionary(version, rules, global_allow_list)
    else:
        raise HTTPException(status_code=404, detail=f"No rule pack found with version {version}")

    toml_file = create_toml_rule_file(generated_toml_dict)
    return FileResponse(toml_file.name, filename="RESC-SECRETS-RULE.toml")


@router.post("",
             status_code=status.HTTP_200_OK)
def upload_rule_pack_toml_file(version: str = Query(default=Required, regex=r"^\d+(?:\.\d+){2}$"),
                               rule_file: UploadFile = File(...),
                               db_connection: Session = Depends(get_db_connection)) -> dict:
    """
        Upload rule pack to database in TOML format
    :param version:
        version of the rule pack to be uploaded
    :param rule_file:
        TOML rule pack file to be uploaded
    :param db_connection:
        Session of the database connection
    :return: dict
        The output returns uploaded rule pack name in dictionary format
    """
    content = validate_uploaded_file_and_read_content(rule_file)
    toml_rule_dictionary = tomlkit.loads(content)

    # Check if rule pack version exists
    rule_pack_from_db = read_rule_pack(version=version, db_connection=db_connection)
    if rule_pack_from_db:
        raise HTTPException(status_code=409, detail=f"Unable to process rules. Rule pack version "
                                                    f"{version} already exists")

    # Insert in to RULE_ALLOW_LIST for storing global allow list
    created_global_rule_allow_list = None
    global_allow_list: RuleAllowList = get_mapped_global_allow_list_obj(toml_rule_dictionary)
    if global_allow_list:
        created_global_rule_allow_list = create_rule_allow_list(rule_allow_list=global_allow_list,
                                                                db_connection=db_connection)
        if not created_global_rule_allow_list.id_:
            logger.warning("Creating global rule allow list failed with an error")

    # # Insert in to RULE_PACK
    global_allow_list_id = created_global_rule_allow_list.id_ if \
        created_global_rule_allow_list and created_global_rule_allow_list.id_ else None

    # Determine if uploaded rule pack needs to be activated
    current_newest_rule_pack = rule_pack_crud.get_newest_rule_pack(db_connection)
    activate_uploaded_rule_pack = determine_uploaded_rule_pack_activation(version, current_newest_rule_pack)

    rule_pack = RulePackCreate(version=version, active=activate_uploaded_rule_pack,
                               global_allow_list=global_allow_list_id)
    created_rule_pack_version = create_rule_pack_version(rule_pack=rule_pack, db_connection=db_connection)
    if created_rule_pack_version.version and activate_uploaded_rule_pack:
        # Update older rule packs to inactive
        rule_pack_crud.make_older_rule_packs_to_inactive(latest_rule_pack_version=version,
                                                         db_connection=db_connection)
    else:
        logger.warning("Creating rule pack failed with an error")

    # Insert in to RULES
    if created_rule_pack_version and created_rule_pack_version.version:
        insert_rules(version=version, toml_rule_dictionary=toml_rule_dictionary,
                     db_connection=db_connection)
    return {"filename": rule_file.filename}


def read_rule_pack(version: Optional[str] = None,
                   db_connection: Session = Depends(get_db_connection)) -> RulePackRead:
    """
        Read active rule pack from database
    :param version:
        optional, version of the rule pack to be fetched else latest rule pack version will be fetched
    :param db_connection:
        Session of the database connection
    :return: RulePackRead
        The output returns RulePackRead type object
    """
    if version:
        regex = re.compile(r"^\d+(?:\.\d+){2}$")
        if not re.fullmatch(regex, version):
            raise HTTPException(status_code=422, detail=f"Version {version} is not a valid semantic version")
    db_rule_pack = rule_pack_crud.get_rule_pack(db_connection=db_connection, version=version)
    return db_rule_pack


def create_rule_pack_version(
        rule_pack: RulePackCreate,
        db_connection: Session = Depends(get_db_connection)):
    """
        Create rule pack version in database
    :param rule_pack:
        RulePackCreate object to be created
    :param db_connection:
        Session of the database connection
    """
    return rule_pack_crud.create_rule_pack_version(db_connection=db_connection,
                                                   rule_pack=rule_pack)


def create_rule_allow_list(
        rule_allow_list: RuleAllowList,
        db_connection: Session = Depends(get_db_connection)):
    """
        Create rule allow list in database
    :param rule_allow_list:
        RuleAllowList object to be created
    :param db_connection:
        Session of the database connection
    """
    if rule_allow_list.paths or rule_allow_list.commits or rule_allow_list.stop_words \
            or rule_allow_list.description or rule_allow_list.regexes:
        return rule_crud.create_rule_allow_list(db_connection=db_connection, rule_allow_list=rule_allow_list)
    raise HTTPException(status_code=400, detail="No properties defined for rule allow list")


def insert_rules(version: str, toml_rule_dictionary: dict, db_connection: Session = Depends(get_db_connection)):
    """
        Create rules in database
    :param version:
        version of the rule pack
    :param toml_rule_dictionary:
        rule pack toml in dictionary format
    :param db_connection:
        Session of the database connection
    """
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
            created_rule = rule_crud.create_rule(rule=rule_obj, db_connection=db_connection)
            if not created_rule.id_:
                logger.warning(f"Creating rule failed for Rule: {rule_name}")


def determine_uploaded_rule_pack_activation(requested_rule_pack_version: str,
                                            latest_rule_pack_from_db: RulePackRead) -> bool:
    """
        Determine if rule pack needs to be activated
    :param requested_rule_pack_version:
        version of the rule pack uploaded
    :param latest_rule_pack_from_db:
        latest rule pack in RulePackRead object
    :return: boolean
        The output returns true if rule pack needs to be activated else returns false
    """
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
