# pylint: disable=R0916,R0912,C0121
# Standard Library
import logging
from datetime import datetime
from typing import List

# Third Party
from sqlalchemy import and_, extract, func, or_
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import scan_finding as scan_finding_crud
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema import finding as finding_schema
from resc_backend.resc_web_service.schema.date_filter import DateFilter
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

logger = logging.getLogger(__name__)


def patch_finding(db_connection: Session, finding_id: int, finding_update: finding_schema.FindingPatch):
    db_finding = db_connection.query(model.DBfinding).filter_by(id_=finding_id).first()

    finding_update_dict = finding_update.dict(exclude_unset=True)
    for key in finding_update_dict:
        setattr(db_finding, key, finding_update_dict[key])

    db_connection.commit()
    db_connection.refresh(db_finding)
    return db_finding


def create_findings(db_connection: Session, findings: List[finding_schema.FindingCreate]) -> List[model.DBfinding]:
    if len(findings) < 1:
        # Function is called with an empty list of findings
        return []
    branch_id = findings[0].branch_id

    # get a list of known / registered findings for this branch
    db_branch_findings = db_connection.query(model.DBfinding).filter(model.DBfinding.branch_id == branch_id).all()

    # Compare new findings list with findings in the db
    new_findings = findings[:]
    db_findings = []
    for finding in findings:
        for branch_finding in db_branch_findings:
            # Compare based on the unique key in the findings table
            if branch_finding.commit_id == finding.commit_id and \
                    branch_finding.rule_name == finding.rule_name and \
                    branch_finding.file_path == finding.file_path and \
                    branch_finding.line_number == finding.line_number and \
                    branch_finding.column_start == finding.column_start and \
                    branch_finding.column_end == finding.column_end:
                # Store the already known finding
                db_findings.append(branch_finding)
                # Remove from the db_branch_findings to increase performance for the next loop
                db_branch_findings.remove(branch_finding)
                # Remove from the to be created findings
                new_findings.remove(finding)
                break
    logger.info(f"create_findings branch {branch_id}, Requested: {len(findings)}. "
                f"New findings: {len(new_findings)}. Already in db: {len(db_findings)}")

    db_create_findings = []
    # Map the to be created findings to the DBfinding type object
    for new_finding in new_findings:
        db_create_finding = model.finding.DBfinding.create_from_finding(new_finding)
        db_create_findings.append(db_create_finding)
    # Store all the to be created findings in the database
    if len(db_create_findings) >= 1:
        db_connection.add_all(db_create_findings)
        db_connection.flush()
        db_connection.commit()
        db_findings.extend(db_create_findings)
    # Return the known findings that are part of the request and the newly created findings
    return db_findings


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

    if statuses_filter:
        # subquery to select latest audit ids findings
        max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                                 func.max(model.DBaudit.id_).label("audit_id")) \
            .group_by(model.DBaudit.finding_id).subquery()

        query = query \
            .join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
                  isouter=True) \
            .join(model.DBaudit, model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id,
                  isouter=True)
        if FindingStatus.NOT_ANALYZED in statuses_filter:
            query = query.filter(or_(model.DBaudit.status.in_(statuses_filter),
                                     model.DBaudit.status == None))  # noqa: E711
        else:
            query = query.filter(model.DBaudit.status.in_(statuses_filter))

    query = query.filter(model.DBscanFinding.scan_id.in_(scan_ids))

    if rules_filter:
        query = query.filter(model.DBfinding.rule_name.in_(rules_filter))

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
        if findings_filter.finding_statuses:
            # subquery to select latest audit ids findings
            max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                                     func.max(model.DBaudit.id_).label("audit_id")) \
                .group_by(model.DBaudit.finding_id).subquery()

            total_count_query = total_count_query \
                .join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
                      isouter=True) \
                .join(model.DBaudit, model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id,
                      isouter=True)
        if (findings_filter.vcs_providers and findings_filter.vcs_providers is not None) \
                or findings_filter.project_name or findings_filter.branch_name \
                or findings_filter.repository_name or findings_filter.start_date_time \
                or findings_filter.end_date_time:
            total_count_query = total_count_query \
                .join(model.DBscanFinding,
                      model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
                .join(model.DBscan,
                      model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
                .join(model.DBbranch,
                      model.branch.DBbranch.id_ == model.scan.DBscan.branch_id) \
                .join(model.DBrepository,
                      model.repository.DBrepository.id_ == model.branch.DBbranch.repository_id) \
                .join(model.DBVcsInstance,
                      model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
        elif findings_filter.rule_tags:
            max_scan_subquery = db_connection.query(model.DBscanFinding.finding_id,
                                                    func.max(model.DBscanFinding.scan_id).label("scan_id"))
            max_scan_subquery = max_scan_subquery.group_by(model.DBscanFinding.finding_id).subquery()
            total_count_query = total_count_query.join(max_scan_subquery,
                                                       model.finding.DBfinding.id_ == max_scan_subquery.c.finding_id) \
                .join(model.DBscan, model.scan.DBscan.id_ == max_scan_subquery.c.scan_id)

        if findings_filter.rule_tags:
            total_count_query = total_count_query.join(model.DBrule,
                                                       and_(model.DBrule.rule_name == model.DBfinding.rule_name,
                                                            model.DBrule.rule_pack == model.DBscan.rule_pack))
            for tag in findings_filter.rule_tags:
                total_count_query = total_count_query.filter(model.DBrule.tags.like(f"%{tag}%"))

        if findings_filter.start_date_time:
            total_count_query = total_count_query.filter(
                model.scan.DBscan.timestamp >= findings_filter.start_date_time)
        if findings_filter.end_date_time:
            total_count_query = total_count_query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_time)

        if findings_filter.branch_name:
            total_count_query = total_count_query.filter(model.DBbranch.branch_name == findings_filter.branch_name)
        if findings_filter.repository_name:
            total_count_query = total_count_query.filter(
                model.DBrepository.repository_name == findings_filter.repository_name)

        if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
            total_count_query = total_count_query.filter(
                model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
        if findings_filter.project_name:
            total_count_query = total_count_query.filter(
                model.repository.DBrepository.project_key == findings_filter.project_name)
        if findings_filter.rule_names:
            total_count_query = total_count_query.filter(model.DBfinding.rule_name.in_(findings_filter.rule_names))
        if findings_filter.finding_statuses:
            if FindingStatus.NOT_ANALYZED in findings_filter.finding_statuses:
                total_count_query = total_count_query.\
                    filter(or_(model.DBaudit.status.in_(findings_filter.finding_statuses),
                               model.DBaudit.status == None))  # noqa: E711
            else:
                total_count_query = total_count_query.filter(model.DBaudit.status.in_(findings_filter.finding_statuses))
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
    findings = db_connection.query(model.DBfinding)
    findings = findings.filter(model.DBfinding.rule_name == rule_name)
    findings = findings.order_by(model.finding.DBfinding.id_).offset(skip).limit(limit_val).all()
    return findings


def get_distinct_rules_from_findings(db_connection: Session, scan_id: int = -1,
                                     finding_statuses: [FindingStatus] = None,
                                     vcs_providers: [VCSProviders] = None,
                                     project_name: str = "",
                                     repository_name: str = "",
                                     start_date_time: datetime = None,
                                     end_date_time: datetime = None,
                                     rule_pack_versions: [str] = None) -> \
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
    :param start_date_time:
        optional, filter on start date
    :param end_date_time:
        optional, filter on end date
    :param rule_pack_versions:
        optional, filter on rule pack version
    :return: rules
        List of unique rules
    """
    query = db_connection.query(model.DBfinding.rule_name)

    if (vcs_providers or project_name or repository_name or start_date_time or end_date_time or rule_pack_versions) \
            and scan_id < 0:
        query = query \
            .join(model.DBscanFinding,
                  model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
            .join(model.DBscan,
                  model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
            .join(model.DBbranch,
                  model.branch.DBbranch.id_ == model.scan.DBscan.branch_id) \
            .join(model.DBrepository,
                  model.repository.DBrepository.id_ == model.branch.DBbranch.repository_id) \
            .join(model.DBVcsInstance,
                  model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
    if finding_statuses:
        # subquery to select latest audit ids findings
        max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                                 func.max(model.DBaudit.id_).label("audit_id")) \
            .group_by(model.DBaudit.finding_id).subquery()

        query = query \
            .join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
                  isouter=True) \
            .join(model.DBaudit, model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id,
                  isouter=True)
    if scan_id > 0:
        query = query.join(model.DBscanFinding,
                           model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
        query = query.filter(model.DBscanFinding.scan_id == scan_id)
    else:
        if finding_statuses:
            if FindingStatus.NOT_ANALYZED in finding_statuses:
                query = query. \
                    filter(or_(model.DBaudit.status.in_(finding_statuses),
                               model.DBaudit.status == None))  # noqa: E711
            else:
                query = query.filter(model.DBaudit.status.in_(finding_statuses))

        if vcs_providers:
            query = query.filter(model.DBVcsInstance.provider_type.in_(vcs_providers))

        if project_name:
            query = query.filter(model.DBrepository.project_key == project_name)

        if repository_name:
            query = query.filter(model.DBrepository.repository_name == repository_name)

        if start_date_time:
            query = query.filter(model.scan.DBscan.timestamp >= start_date_time)

        if end_date_time:
            query = query.filter(model.scan.DBscan.timestamp <= end_date_time)

        if rule_pack_versions:
            query = query.filter(model.DBscan.rule_pack.in_(rule_pack_versions))

    rules = query.distinct().order_by(model.DBfinding.rule_name).all()
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
    # subquery to select latest audit ids findings
    max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                             func.max(model.DBaudit.id_).label("audit_id")) \
        .group_by(model.DBaudit.finding_id).subquery()

    query = db_connection.query(func.count(model.DBfinding.id_).label('status_count'), model.DBaudit.status)

    query = query \
        .join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
              isouter=True) \
        .join(model.DBaudit, model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id,
              isouter=True)

    if scan_ids and len(scan_ids) > 0:
        query = query \
            .join(model.DBscanFinding,
                  model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
            .join(model.DBscan,
                  model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
            .filter(model.DBscan.id_.in_(scan_ids))
    if finding_statuses:
        query = query.filter(model.DBaudit.status.in_(finding_statuses))
    if rule_name:
        query = query.filter(model.DBfinding.rule_name == rule_name)

    findings_count_by_status = query.group_by(model.DBaudit.status).all()

    return findings_count_by_status


def get_findings_count_by_time(db_connection: Session,
                               date_type: DateFilter,
                               start_date_time: datetime = None,
                               end_date_time: datetime = None,
                               skip: int = 0,
                               limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT):
    """
        Retrieve count based on date_type
    :param db_connection:
        Session of the database connection
    :param date_type:
        required, filter on time_type
    :param start_date_time:
        optional, filter on start date
    :param end_date_time:
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

    if start_date_time:
        query = query.filter(model.DBscan.timestamp >= start_date_time)
    if end_date_time:
        query = query.filter(model.DBscan.timestamp <= end_date_time)

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
                                     start_date_time: datetime = None,
                                     end_date_time: datetime = None):
    """
        Retrieve total count on date_type
    :param db_connection:
        Session of the database connection
    :param date_type:
        required, filter on time_type
    :param start_date_time:
        optional, filter on start date
    :param end_date_time:
        optional, filter on end date
    """
    if date_type == DateFilter.MONTH:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp))
    elif date_type == DateFilter.WEEK:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('week', model.DBscan.timestamp))
    elif date_type == DateFilter.DAY:
        query = db_connection.query(extract('year', model.DBscan.timestamp), extract('month', model.DBscan.timestamp),
                                    extract('day', model.DBscan.timestamp))

    if start_date_time:
        query = query.filter(model.DBscan.timestamp >= start_date_time)
    if end_date_time:
        query = query.filter(model.DBscan.timestamp <= end_date_time)

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
    query = db_connection.query(model.DBfinding.rule_name)

    if scan_ids:
        query = query.join(model.DBscanFinding,
                           model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_)
        query = query.filter(model.DBscanFinding.scan_id.in_(scan_ids))

    rules = query.distinct().order_by(model.DBfinding.rule_name).all()
    return rules


def delete_finding(db_connection: Session, finding_id: int, delete_related: bool = False):
    """
        Delete a finding object
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to be deleted
    :param delete_related:
        if related records need to be deleted
    """
    if delete_related:
        scan_finding_crud.delete_scan_finding(db_connection, finding_id=finding_id)

    db_connection.query(model.DBfinding) \
        .filter(model.finding.DBfinding.id_ == finding_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_findings_by_branch_id(db_connection: Session, branch_id: int):
    """
        Delete findings for a given branch
    :param db_connection:
        Session of the database connection
    :param branch_id:
        id of the branch
    """
    db_connection.query(model.DBfinding) \
        .filter(model.finding.DBfinding.branch_id == branch_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_findings_by_repository_id(db_connection: Session, repository_id: int):
    """
        Delete findings for a given repository
    :param db_connection:
        Session of the database connection
    :param repository_id:
        id of the repository
    """
    db_connection.query(model.DBfinding) \
        .filter(model.finding.DBfinding.branch_id == model.branch.DBbranch.id_,
                model.branch.DBbranch.repository_id == model.repository.DBrepository.id_,
                model.repository.DBrepository.id_ == repository_id) \
        .delete(synchronize_session=False)
    db_connection.commit()


def delete_findings_by_vcs_instance_id(db_connection: Session, vcs_instance_id: int):
    """
        Delete findings for a given vcs instance
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the vcs instance
    """
    db_connection.query(model.DBfinding) \
        .filter(model.finding.DBfinding.branch_id == model.branch.DBbranch.id_,
                model.branch.DBbranch.repository_id == model.repository.DBrepository.id_,
                model.repository.DBrepository.vcs_instance == model.vcs_instance.DBVcsInstance.id_,
                model.vcs_instance.DBVcsInstance.id_ == vcs_instance_id) \
        .delete(synchronize_session=False)
    db_connection.commit()
