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
    Returns the rule pack information of the specified version if specified, return that of the active one otherwise.
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
    rule_packs = db_connection.query(model.DBrulePack).all()
    newest_rule_pack = None
    if rule_packs:
        newest_rule_pack: rule_pack_schema.RulePackRead = rule_packs[0]
        for rule_pack in rule_packs[1:]:
            if Version(rule_pack.version) > Version(newest_rule_pack.version):
                newest_rule_pack = rule_pack
    return newest_rule_pack


def get_rule_packs(db_connection: Session, version: str = None, skip: int = 0,
                   limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> List[model.rule_pack.DBrulePack]:
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.rule_pack.DBrulePack)

    if version:
        query = query.filter(model.rule_pack.DBrulePack.version == version)
    rule_packs = query.order_by(model.rule_pack.DBrulePack.version).offset(skip).limit(limit_val).all()
    return rule_packs


def get_total_rule_packs_count(db_connection: Session, version: str = None) -> int:
    total_count_query = db_connection.query(func.count(model.rule_pack.DBrulePack.version))
    if version:
        total_count_query = total_count_query.filter(model.rule_pack.DBrulePack.version == version)

    total_count = total_count_query.scalar()
    return total_count


def make_older_rule_packs_to_inactive(latest_rule_pack_version: str, db_connection: Session):
    db_connection.execute(update(model.rule_pack.DBrulePack)
                          .where(model.rule_pack.DBrulePack.version != latest_rule_pack_version)
                          .values(active=False))
    db_connection.commit()
