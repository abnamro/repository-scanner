# pylint: disable=R0916,R0912
# Standard Library
import logging
from datetime import datetime
from typing import List

# Third Party
from sqlalchemy import extract, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema import finding as finding_schema
from resc_backend.resc_web_service.schema.date_filter import DateFilter
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

logger = logging.getLogger(__name__)


def update_finding(db_connection: Session, finding_id: int, finding: finding_schema.FindingCreate):
    db_finding = db_connection.query(model.DBfinding).filter_by(id_=finding_id).first()
    db_finding.file_path = finding.file_path
    db_finding.line_number = finding.line_number
    db_finding.commit_id = finding.commit_id
    db_finding.commit_message = finding.commit_message
    db_finding.commit_timestamp = finding.commit_timestamp
    db_finding.author = finding.author
    db_finding.email = finding.email
    db_finding.status = finding.status
    db_finding.comment = finding.comment
    db_finding.event_sent_on = finding.event_sent_on

    db_connection.commit()
    db_connection.refresh(db_finding)
    return db_finding


def patch_finding(db_connection: Session, finding_id: int, finding_update: finding_schema.FindingUpdate):
    db_finding = db_connection.query(model.DBfinding).filter_by(id_=finding_id).first()

    finding_update_dict = finding_update.dict(exclude_unset=True)
    for key in finding_update_dict:
        setattr(db_finding, key, finding_update_dict[key])

    db_connection.commit()
    db_connection.refresh(db_finding)
    return db_finding


def audit_finding(db_connection: Session, db_finding: finding_schema.FindingRead,
                  status: FindingStatus, comment: str = "") -> model.DBfinding:
    """
        Audit finding, updating the status and comment
    :param db_connection:
        Session of the database connection
    :param db_finding:
        database finding object to update
    :param status:
        audit status to set, type FindingStatus
    :param comment:
        audit comment to set
    :return: FindingRead
        The output will contain the findings that was updated
    """
    db_finding.status = status
    db_finding.comment = comment

    db_connection.commit()
    db_connection.refresh(db_finding)
    return db_finding


def create_findings(db_connection: Session, findings: List[finding_schema.FindingCreate]) -> List[model.DBfinding]:
    db_findings = []
    if len(findings) < 1:
        # Function is called with an empty list of findings
        return []

    for finding in findings:
        db_finding = model.finding.DBfinding.create_from_finding(finding)

        try:
            with db_connection.begin_nested():
                db_connection.add(db_finding)
                db_connection.flush()
            db_connection.commit()
            db_connection.refresh(db_finding)

        except IntegrityError as integrity_error:

            if "uc_finding_per_branch" not in str(integrity_error):
                raise integrity_error
            logger.warning(f"Already existing finding in branch: '{db_finding.branch_info_id}' "
                           f"filepath: '{db_finding.file_path}' for rule: '{db_finding.rule_name}' was ignored")
            db_finding = db_connection.query(model.DBfinding).filter_by(
                file_path=db_finding.file_path,
                branch_info_id=db_finding.branch_info_id,
                line_number=db_finding.line_number,
                rule_name=db_finding.rule_name,
                commit_id=db_finding.commit_id
            ).first()
        db_findings.append(db_finding)
    return db_findings


def delete_finding(db_connection: Session, finding_id: int):
    db_finding = db_connection.query(model.DBfinding).filter_by(id_=finding_id).first()
    db_connection.delete(db_finding)
    db_connection.commit()
    return db_finding


def get_finding(db_connection: Session, finding_id: int):
    finding = db_connection.query(model.DBfinding)
    finding = finding.filter(model.finding.DBfinding.id_ == finding_id).first()
    return finding


def get_findings(db_connection: Session, skip: int = 0,
                 limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT):
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    findings = db_connection.query(model.DBfinding)
    findings = findings.order_by(model.finding.DBfinding.id_).offset(skip).limit(limit_val).all()
    return findings


def get_scan_findings(db_connection, scan_id: int, skip: int = 0, limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT,
                      rule_filter: str = "", status_filter: FindingStatus = None) -> [model.DBfinding]:
    """
        Retrieve all finding child objects of a scan object from the database
    :param db_connection:
        Session of the database connection
    :param scan_id:
        id of the parent scan object of which to retrieve finding objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param rule_filter:
        optional, filter on rule name. Is used as a string contains filter
    :param status_filter:
        optional, filter on status of findings
    :return: [DBfinding]
        The output will contain a list of DBfinding type objects,
        or an empty list if no finding was found for the given scan_id
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.DBfinding)

    if rule_filter:
        query = query.join(model.DBrule, model.DBfinding.rule_id == model.DBrule.id_)
        query = query.filter(model.DBrule.rule_name.ilike(f"%{rule_filter}%"))
        query = query.join(model.DBscanFinding,
                           model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
        query = query.filter(model.DBscanFinding.scan_id == scan_id)

    if status_filter:
        query = query.filter(model.DBfinding.status == status_filter)

    findings = query.order_by(model.finding.DBfinding.id_).offset(skip).limit(limit_val).all()
    return findings


def get_scans_findings(db_connection, scan_ids: [int], skip: int = 0, limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT,
                       rules_filter: [str] = None, statuses_filter: [FindingStatus] = None) -> [model.DBfinding]:
    """
        Retrieve all finding child objects of a scan object from the database
    :param db_connection:
        Session of the database connection
    :param scan_ids:
        ids of the parent scan object of which to retrieve finding objects
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param rules_filter:
        optional, filter on rule name. Is used as a string contains filter
    :param statuses_filter:
        optional, filter on status of findings
    :return: [DBfinding]
        The output will contain a list of DBfinding type objects,
        or an empty list if no finding was found for the given scan_ids
    """
    if len(scan_ids) == 0:
        return []
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit

    query = db_connection.query(model.DBfinding)
    query = query.join(model.DBscanFinding,
                       model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)

    query = query.filter(model.DBscanFinding.scan_id.in_(scan_ids))

    if rules_filter:
        query = query.filter(model.DBfinding.rule_name.in_(rules_filter))

    if statuses_filter:
        query = query.filter(model.DBfinding.status.in_(statuses_filter))

    findings = query.order_by(model.finding.DBfinding.id_).offset(skip).limit(limit_val).all()
    return findings


def get_total_findings_count(db_connection: Session, findings_filter: FindingsFilter = None) -> int:
    """
        Retrieve count of finding records of a given scan
    :param findings_filter:
    :param db_connection:
        Session of the database connection
    :return: total_count
        count of findings
    """

    total_count_query = db_connection.query(func.count(model.DBfinding.id_))
    if findings_filter:
        if findings_filter.rule_names:
            total_count_query = total_count_query.join(
                model.DBrule, model.DBfinding.rule_name == model.DBrule.rule_name)

        if (findings_filter.vcs_providers and findings_filter.vcs_providers is not None) \
                or findings_filter.project_name or findings_filter.branch_name \
                or findings_filter.repository_name or findings_filter.start_date_range \
                or findings_filter.end_date_range:
            total_count_query = total_count_query \
                .join(model.DBscanFinding,
                      model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
                .join(model.DBscan,
                      model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
                .join(model.DBbranchInfo,
                      model.branch_info.DBbranchInfo.id_ == model.scan.DBscan.branch_info_id) \
                .join(model.DBrepositoryInfo,
                      model.repository_info.DBrepositoryInfo.id_ == model.branch_info.DBbranchInfo.repository_info_id) \
                .join(model.DBVcsInstance,
                      model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)

        if findings_filter.start_date_range:
            total_count_query = total_count_query.filter(
                model.scan.DBscan.timestamp >= findings_filter.start_date_range)
        if findings_filter.end_date_range:
            total_count_query = total_count_query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_range)

        if findings_filter.branch_name:
            total_count_query = total_count_query.filter(model.DBbranchInfo.branch_name == findings_filter.branch_name)
        if findings_filter.repository_name:
            total_count_query = total_count_query.filter(
                model.DBrepositoryInfo.repository_name == findings_filter.repository_name)

        if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
            total_count_query = total_count_query.filter(
                model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
        if findings_filter.project_name:
            total_count_query = total_count_query.filter(
                model.repository_info.DBrepositoryInfo.project_key == findings_filter.project_name)
        if findings_filter.rule_names:
            total_count_query = total_count_query.filter(model.DBrule.rule_name.in_(findings_filter.rule_names))
        if findings_filter.finding_statuses:
            total_count_query = total_count_query.filter(
                model.finding.DBfinding.status.in_(findings_filter.finding_statuses))
        if findings_filter.scan_ids and len(findings_filter.scan_ids) == 1:
            total_count_query = total_count_query.join(
                model.DBscanFinding, model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
            total_count_query = total_count_query.filter(
                model.scan_finding.DBscanFinding.scan_id == findings_filter.scan_ids[0])

        if findings_filter.scan_ids and len(findings_filter.scan_ids) >= 2:
            total_count_query = total_count_query.join(
                model.DBscanFinding, model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
            total_count_query = total_count_query.filter(
                model.scan_finding.DBscanFinding.scan_id.in_(findings_filter.scan_ids))

    total_count = total_count_query.scalar()
    return total_count


def get_findings_by_rule(db_connection: Session, skip: int = 0, limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT,
                         rule_name: str = ""):
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    findings = db_connection.query(model.DBfinding, model.DBrule.rule_name)
    findings = findings.join(model.DBrule, model.DBfinding.rule_id == model.DBrule.id_)
    findings = findings.filter(model.DBrule.rule_name == rule_name)
    findings = findings.order_by(model.finding.DBfinding.id_).offset(skip).limit(limit_val).all()
    return findings


def get_distinct_rules_from_findings(db_connection: Session, scan_id: int = -1,
                                     finding_statuses: [FindingStatus] = None,
                                     vcs_providers: [VCSProviders] = None,
                                     project_name: str = "",
                                     repository_name: str = "",
                                     start_date: datetime = None,
                                     end_date: datetime = None) -> \
        List[model.DBrule]:
    """
        Retrieve distinct rules detected
    :param db_connection:
        Session of the database connection
    :param scan_id:
        Optional filter by the id of a scan
    :param finding_statuses:
        Optional, filter of supported finding statuses
    :param vcs_providers:
        Optional, filter of supported vcs provider types
    :param project_name:
        Optional, filter on project name. Is used as a full string match filter
    :param repository_name:
        optional, filter on repository name. Is used as a string contains filter
    :param start_date:
        optional, filter on start date
    :param end_date:
        optional, filter on end date
    :return: rules
        List of unique rules
    """
    query = db_connection.query(model.DBrule.rule_name)
    query = query.join(model.DBfinding, model.DBfinding.rule_name == model.DBrule.rule_name)

    if (vcs_providers or project_name or repository_name or start_date or end_date) and scan_id < 0:
        query = query \
            .join(model.DBscanFinding,
                  model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
            .join(model.DBscan,
                  model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
            .join(model.DBbranchInfo,
                  model.branch_info.DBbranchInfo.id_ == model.scan.DBscan.branch_info_id) \
            .join(model.DBrepositoryInfo,
                  model.repository_info.DBrepositoryInfo.id_ == model.branch_info.DBbranchInfo.repository_info_id) \
            .join(model.DBVcsInstance,
                  model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)

    if scan_id > 0:
        query = query.join(model.DBscanFinding,
                           model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
        query = query.filter(model.DBscanFinding.scan_id == scan_id)
    else:
        if finding_statuses:
            query = query.filter(model.DBfinding.status.in_(finding_statuses))

        if vcs_providers:
            query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

        if project_name:
            query = query.filter(model.DBrepositoryInfo.project_key == project_name)

        if repository_name:
            query = query.filter(model.DBrepositoryInfo.repository_name == repository_name)

        if start_date:
            query = query.filter(model.scan.DBscan.timestamp >= start_date)

        if end_date:
            query = query.filter(model.scan.DBscan.timestamp <= end_date)

    rules = query.distinct().order_by(model.DBrule.rule_name).all()
    return rules


def get_findings_count_by_status(db_connection: Session, scan_ids: List[int] = None,
                                 finding_statuses: [FindingStatus] = None, rule_name: str = ""):
    """
        Retrieve count of findings based on finding status
    :param db_connection:
        Session of the database connection
    :param scan_ids:
        List of scan ids for which findings should be filtered
    :param finding_statuses:
        finding statuses to filter, type FindingStatus
    :param rule_name:
        rule_name to filter on
    :return: findings_count
        count of findings
    """
    query = db_connection.query(model.DBfinding.status, func.count(model.DBfinding.status).label('status_count'))

    if rule_name:
        query = query.join(model.DBrule, model.DBfinding.rule_name == model.DBrule.rule_name)

    if scan_ids and len(scan_ids) > 0:
        query = query \
            .join(model.DBscanFinding,
                  model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
            .join(model.DBscan,
                  model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
            .filter(model.DBscan.id_.in_(scan_ids))
    if finding_statuses:
        query = query.filter(model.DBfinding.status.in_(finding_statuses))
    if rule_name:
        query = query.filter(model.DBrule.rule_name == rule_name)

    findings_count_by_status = query.group_by(model.DBfinding.status).all()

    return findings_count_by_status


def get_findings_count_by_time(db_connection: Session,
                               date_type: DateFilter,
                               start_date: datetime = None,
                               end_date: datetime = None,
                               skip: int = 0,
                               limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT):
    """
        Retrieve count based on date_type
    :param db_connection:
        Session of the database connection
    :param date_type:
        required, filter on time_type
    :param start_date:
        optional, filter on start date
    :param end_date:
        optional, filter on end date
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    """
    if date_type == DateFilter.MONTH:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                                    func.count(model.DBscanFinding.finding_id))
    elif date_type == DateFilter.WEEK:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('week', model.DBscan.timestamp),
                                    func.count(model.DBscanFinding.finding_id))
    elif date_type == DateFilter.DAY:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                                    extract('day', model.DBscan.timestamp), func.count(model.DBscanFinding.finding_id))

    query = query.join(model.DBscanFinding, model.DBscanFinding.scan_id == model.DBscan.id_)

    if start_date:
        query = query.filter(model.DBscan.timestamp >= start_date)
    if end_date:
        query = query.filter(model.DBscan.timestamp <= end_date)

    if date_type == DateFilter.MONTH:
        query = query.group_by(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp))
        query = query.order_by(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp))
    elif date_type == DateFilter.WEEK:
        query = query.group_by(extract('year', model.DBscan.timestamp), extract('week', model.DBscan.timestamp))
        query = query.order_by(extract('year', model.DBscan.timestamp), extract('week', model.DBscan.timestamp))
    elif date_type == DateFilter.DAY:
        query = query.group_by(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                               extract('day', model.DBscan.timestamp))
        query = query.order_by(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                               extract('day', model.DBscan.timestamp))

    finding_count = query.offset(skip).limit(limit).all()
    return finding_count


def get_findings_count_by_time_total(db_connection: Session,
                                     date_type: DateFilter,
                                     start_date: datetime = None,
                                     end_date: datetime = None):
    """
        Retrieve total count on date_type
    :param db_connection:
        Session of the database connection
    :param date_type:
        required, filter on time_type
    :param start_date:
        optional, filter on start date
    :param end_date:
        optional, filter on end date
    """
    if date_type == DateFilter.MONTH:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp))
    elif date_type == DateFilter.WEEK:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('week', model.DBscan.timestamp))
    elif date_type == DateFilter.DAY:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                                    extract('day', model.DBscan.timestamp))

    if start_date:
        query = query.filter(model.DBscan.timestamp >= start_date)
    if end_date:
        query = query.filter(model.DBscan.timestamp <= end_date)

    query = query.distinct()

    result = query.count()
    return result


def get_distinct_rules_from_scans(db_connection: Session, scan_ids: List[int] = None) -> \
        List[model.DBrule]:
    """
        Retrieve distinct rules detected
    :param db_connection:
        Session of the database connection
    :param scan_ids:
        List of scan ids
    :return: rules
        List of unique rules
    """
    query = db_connection.query(model.DBrule.rule_name)
    query = query.join(model.DBfinding, model.DBfinding.rule_name == model.DBrule.rule_name)

    if scan_ids:
        query = query.join(model.DBscanFinding,
                           model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
        query = query.filter(model.DBscanFinding.scan_id.in_(scan_ids))

    rules = query.distinct().order_by(model.DBrule.rule_name).all()
    return rules
