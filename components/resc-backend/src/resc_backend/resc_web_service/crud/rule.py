# Standard Library
import logging
from typing import List

# Third Party
from packaging.version import Version
from sqlalchemy.orm import Session

# First Party
from resc_backend.db import model
from resc_backend.resc_web_service.schema import rule_allow_list as rule_allow_list_schema
from resc_backend.resc_web_service.schema import rule_pack as rule_pack_schema
from resc_backend.resc_web_service.schema.rule import RuleCreate, RuleRead

logger = logging.getLogger(__name__)


def get_rules_by_scan_id(db_connection: Session, scan_id: int) -> List[RuleRead]:
    rule_query = db_connection.query(model.DBrule)
    rule_query = rule_query.join(model.DBscan, model.DBscan.rule_pack == model.DBrule.rule_pack)
    rule_query = rule_query.filter(model.DBscan.id_ == scan_id)
    rules: List[RuleRead] = rule_query.all()
    return rules


def get_newest_rule_pack(db_connection: Session) -> rule_pack_schema.RulePackRead:

    rule_packs = db_connection.query(model.DBrulePack).all()
    newest_rule_pack = None
    if rule_packs:
        newest_rule_pack: rule_pack_schema.RulePackRead = rule_packs[0]
        for rule_pack in rule_packs[1:]:
            if Version(rule_pack.version) > Version(newest_rule_pack.version):
                newest_rule_pack = rule_pack
    return newest_rule_pack


def create_rule_allow_list(db_connection: Session, rule_allow_list: rule_allow_list_schema.RuleAllowList):
    db_rule_allow_list = model.rule_allow_list.DBruleAllowList(
        description=rule_allow_list.description,
        regexes=rule_allow_list.regexes,
        paths=rule_allow_list.paths,
        commits=rule_allow_list.commits,
        stop_words=rule_allow_list.stop_words
    )
    db_connection.add(db_rule_allow_list)
    db_connection.commit()
    db_connection.refresh(db_rule_allow_list)
    return db_rule_allow_list


# def create_rule_pack_version(db_connection: Session, rule_pack: rule_pack_schema.RulePackCreate):
#     db_rule_pack = model.rule_pack.DBrulePack(
#         version=rule_pack.version,
#         global_allow_list=rule_pack.global_allow_list,
#         active=rule_pack.active
#     )
#     db_connection.add(db_rule_pack)
#     db_connection.commit()
#     db_connection.refresh(db_rule_pack)
#     return db_rule_pack


def create_rule(db_connection: Session, rule: RuleCreate):
    db_rule = model.rule.DBrule(
        rule_name=rule.rule_name,
        description=rule.description,
        tags=rule.tags,
        entropy=rule.entropy,
        secret_group=rule.secret_group,
        regex=rule.regex,
        path=rule.path,
        keywords=rule.keywords,
        rule_pack=rule.rule_pack,
        allow_list=rule.allow_list,

    )
    db_connection.add(db_rule)
    db_connection.commit()
    db_connection.refresh(db_rule)
    return db_rule


# def get_rule_pack(db_connection: Session, version: Optional[str]) -> rule_pack_schema.RulePackRead:
#     """
#     Returns the rule pack information of the specified version if specified, return that of the active one otherwise.
#     """
#     query = db_connection.query(model.rule_pack.DBrulePack)
#     if version:
#         query = query.filter(model.rule_pack.DBrulePack.version == version)
#     else:
#         logger.debug("rule pack version not specified, fetching currently active one")
#         query = query.filter(model.rule_pack.DBrulePack.active == true())
#     rule_pack = query.first()
#     return rule_pack


# def get_all_rule_packs(db_connection: Session, skip: int = 0,
#                        limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> List[model.rule_pack.DBrulePack]:
#     limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
#     query = db_connection.query(model.rule_pack.DBrulePack)
#
#     rule_packs = query.order_by(model.rule_pack.DBrulePack.version).offset(skip).limit(limit_val).all()
#     return rule_packs


# def get_rule_packs_count(db_connection: Session) -> int:
#     query = db_connection.query(func.count(model.rule_pack.DBrulePack.version))
#
#     total_count = query.scalar()
#     return total_count


def get_rules_by_rule_pack_version(db_connection: Session, rule_pack_version: str) -> List[str]:
    query = db_connection.query(
        model.DBrule.id_,
        model.DBrule.rule_pack,
        model.DBrule.rule_name,
        model.DBrule.tags,
        model.DBrule.entropy,
        model.DBrule.secret_group,
        model.DBrule.regex,
        model.DBrule.path,
        model.DBrule.keywords,
        model.rule_allow_list.DBruleAllowList.description,
        model.rule_allow_list.DBruleAllowList.regexes,
        model.rule_allow_list.DBruleAllowList.paths,
        model.rule_allow_list.DBruleAllowList.commits,
        model.rule_allow_list.DBruleAllowList.stop_words) \
        .join(model.rule_pack.DBrulePack,
              model.rule_pack.DBrulePack.version == model.rule.DBrule.rule_pack) \
        .join(model.rule_allow_list.DBruleAllowList,
              model.rule_allow_list.DBruleAllowList.id_ == model.rule.DBrule.allow_list, isouter=True)
    db_rules = query.filter(model.rule.DBrule.rule_pack == rule_pack_version).order_by(
        model.rule.DBrule.id_).all()
    return db_rules


def get_global_allow_list_by_rule_pack_version(db_connection: Session, rule_pack_version: str) -> List[str]:
    query = db_connection.query(
        model.rule_pack.DBrulePack.version,
        model.rule_allow_list.DBruleAllowList.description,
        model.rule_allow_list.DBruleAllowList.regexes,
        model.rule_allow_list.DBruleAllowList.paths,
        model.rule_allow_list.DBruleAllowList.commits,
        model.rule_allow_list.DBruleAllowList.stop_words) \
        .join(model.rule_allow_list.DBruleAllowList,
              model.rule_allow_list.DBruleAllowList.id_ == model.rule_pack.DBrulePack.global_allow_list)
    db_global_allow_list = query.filter(
        model.rule_pack.DBrulePack.version == rule_pack_version).order_by(
        model.rule_allow_list.DBruleAllowList.id_).first()
    return db_global_allow_list


# def make_older_rule_packs_to_inactive(latest_rule_pack_version: str, db_connection: Session):
#     db_connection.execute(update(model.rule_pack.DBrulePack)
#                           .where(model.rule_pack.DBrulePack.version != latest_rule_pack_version)
#                           .values(active=False))
#     db_connection.commit()
