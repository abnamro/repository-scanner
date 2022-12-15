# Standard Library
import logging
from typing import List, Optional

# Third Party
from packaging.version import Version
from sqlalchemy import func, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.schema import rule_pack as rule_pack_schema

logger = logging.getLogger(__name__)


def get_rule_pack(db_connection: Session, version: Optional[str]) -> rule_pack_schema.RulePackRead:
    """
        Get active rule pack from database
    :param db_connection:
        Session of the database connection
    :param version:
        optional, version of the rule pack to be fetched else latest rule pack version will be fetched
    :return: RulePackRead
        The output returns RulePackRead type object
    """
    query = db_connection.query(model.rule_pack.DBrulePack)
    if version:
        query = query.filter(model.rule_pack.DBrulePack.version == version)
    else:
        logger.debug("rule pack version not specified, fetching currently active one")
        query = query.filter(model.rule_pack.DBrulePack.active == true())
    rule_pack = query.first()
    return rule_pack


def create_rule_pack_version(db_connection: Session, rule_pack: rule_pack_schema.RulePackCreate):
    """
        Create rule pack version in database
    :param db_connection:
        Session of the database connection
    :param rule_pack:
        RulePackCreate object to be created
    """
    db_rule_pack = model.rule_pack.DBrulePack(
        version=rule_pack.version,
        global_allow_list=rule_pack.global_allow_list,
        active=rule_pack.active
    )
    db_connection.add(db_rule_pack)
    db_connection.commit()
    db_connection.refresh(db_rule_pack)
    return db_rule_pack


def get_newest_rule_pack(db_connection: Session) -> rule_pack_schema.RulePackRead:
    """
        Fetch the newest rule pack from database
    :param db_connection:
        Session of the database connection
    :return: RulePackRead
        The output returns RulePackRead type object
    """
    rule_packs = db_connection.query(model.DBrulePack).all()
    newest_rule_pack = None
    if rule_packs:
        newest_rule_pack: rule_pack_schema.RulePackRead = rule_packs[0]
        for rule_pack in rule_packs[1:]:
            if Version(rule_pack.version) > Version(newest_rule_pack.version):
                newest_rule_pack = rule_pack
    return newest_rule_pack


def get_rule_packs(db_connection: Session, version: str = None, active: bool = None, skip: int = 0,
                   limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> List[model.rule_pack.DBrulePack]:
    """
        Retrieve rule packs from database
    :param db_connection:
        Session of the database connection
    :param version:
        optional, filter on rule pack version
    :param active:
        optional, filter on active rule pack
    :param skip:
        integer amount of records to skip, to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [RulePackRead]
        The output will contain a PaginationModel containing the list of RulePackRead type objects,
        or an empty list if no rule pack was found
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.rule_pack.DBrulePack)

    if version:
        query = query.filter(model.rule_pack.DBrulePack.version == version)
    if active is not None:
        query = query.filter(model.rule_pack.DBrulePack.active == active)
    rule_packs = query.order_by(model.rule_pack.DBrulePack.version.desc()).offset(skip).limit(limit_val).all()
    return rule_packs


def get_total_rule_packs_count(db_connection: Session, version: str = None, active: bool = None) -> int:
    """
        Retrieve total count of rule packs from database
    :param db_connection:
        Session of the database connection
    :param version:
        optional, filter on rule pack version
    :param active:
        optional, filter on active rule pack
    :return: int
        The output contains total count of rule packs
    """
    total_count_query = db_connection.query(func.count(model.rule_pack.DBrulePack.version))
    if version:
        total_count_query = total_count_query.filter(model.rule_pack.DBrulePack.version == version)
    if active is not None:
        total_count_query = total_count_query.filter(model.rule_pack.DBrulePack.active == active)

    total_count = total_count_query.scalar()
    return total_count


def make_older_rule_packs_to_inactive(latest_rule_pack_version: str, db_connection: Session):
    """
        Make older rule packs to inactive
    :param latest_rule_pack_version:
        latest rule pack version
    :param db_connection:
        Session of the database connection
    """
    db_connection.execute(update(model.rule_pack.DBrulePack)
                          .where(model.rule_pack.DBrulePack.version != latest_rule_pack_version)
                          .values(active=False))
    db_connection.commit()
