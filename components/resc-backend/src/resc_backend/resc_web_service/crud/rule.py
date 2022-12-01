# Standard Library
import logging
from typing import List

# Third Party
from sqlalchemy.orm import Session

# First Party
from resc_backend.db import model
from resc_backend.resc_web_service.schema import rule_allow_list as rule_allow_list_schema
from resc_backend.resc_web_service.schema.rule import RuleCreate, RuleRead

logger = logging.getLogger(__name__)


def get_rules_by_scan_id(db_connection: Session, scan_id: int) -> List[RuleRead]:
    """
        Get rules by scan id
    :param db_connection:
        Session of the database connection
    :param scan_id:
        scan id for which rules need to be fetched
    :return: List[RuleRead]
        The output contains list of rules
    """
    rule_query = db_connection.query(model.DBrule)
    rule_query = rule_query.join(model.DBscan, model.DBscan.rule_pack == model.DBrule.rule_pack)
    rule_query = rule_query.filter(model.DBscan.id_ == scan_id)
    rules: List[RuleRead] = rule_query.all()
    return rules


def create_rule_allow_list(db_connection: Session, rule_allow_list: rule_allow_list_schema.RuleAllowList):
    """
        Create rule allow list in database
    :param db_connection:
        Session of the database connection
    :param rule_allow_list:
        RuleAllowList object to be created
    """
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


def create_rule(db_connection: Session, rule: RuleCreate):
    """
        Create rule in database
    :param db_connection:
        Session of the database connection
    :param rule:
        RuleCreate object to be created
    """
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


def get_rules_by_rule_pack_version(db_connection: Session, rule_pack_version: str) -> List[str]:
    """
        Fetch rules by rule pack version
    :param db_connection:
        Session of the database connection
    :param rule_pack_version:
        rule pack version
    :return: List[str]
        The output contains list of strings of global allow list
    """
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
    """
        Retrieve global allow list by rule pack version
    :param db_connection:
        Session of the database connection
    :param rule_pack_version:
        rule pack version
    :return: List[str]
        The output contains list of strings of global allow list
    """
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
