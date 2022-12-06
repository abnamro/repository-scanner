# pylint: disable=R0912
# Standard Library
from typing import List

# Third Party
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema import detailed_finding as detailed_finding_schema


def get_detailed_findings(db_connection: Session, findings_filter: FindingsFilter, skip: int = 0,
                          limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT
                          ) -> List[detailed_finding_schema.DetailedFindingRead]:
    """
    Retrieve all detailed findings objects matching the provided FindingsFilter
    :param findings_filter:
        Object of type FindingsFilter, only DetailedFindingRead objects matching the attributes in this filter will be
            fetched
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DetailedFindingRead]
        The output will contain a list of DetailedFindingRead objects,
        or an empty list if no finding was found for the given findings_filter
    """
    max_scan_subquery = db_connection.query(model.DBscanFinding.finding_id,
                                            func.max(model.DBscanFinding.scan_id).label("scan_id"))
    if findings_filter.scan_ids:
        max_scan_subquery = max_scan_subquery.filter(model.DBscanFinding.scan_id.in_(findings_filter.scan_ids))
    max_scan_subquery = max_scan_subquery.group_by(model.DBscanFinding.finding_id).subquery()

    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    scan_id = model.DBscan.id_.label("scan_id")
    query = db_connection.query(
        model.DBfinding.id_,
        model.DBfinding.file_path,
        model.DBfinding.line_number,
        model.DBfinding.commit_id,
        model.DBfinding.commit_message,
        model.DBfinding.commit_timestamp,
        model.DBfinding.author,
        model.DBfinding.email,
        model.DBfinding.status,
        model.DBfinding.comment,
        model.DBfinding.rule_name,
        model.DBscan.rule_pack,
        model.DBfinding.event_sent_on,
        model.DBscan.timestamp,
        scan_id,
        model.DBbranch.branch_name,
        model.DBscan.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepository.project_key,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
    ).join(max_scan_subquery, model.finding.DBfinding.id_ == max_scan_subquery.c.finding_id)\
        .join(model.DBscan,
              model.scan.DBscan.id_ == max_scan_subquery.c.scan_id) \
        .join(model.DBbranch,
              model.branch.DBbranch.id_ == model.finding.DBfinding.branch_id) \
        .join(model.DBrepository,
              model.repository.DBrepository.id_ == model.branch.DBbranch.repository_id)\
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)

    if findings_filter.rule_tags:
        query = query.join(model.DBrule, and_(model.DBrule.rule_name == model.DBfinding.rule_name,
                                              model.DBrule.rule_pack == model.DBscan.rule_pack))
        for tag in findings_filter.rule_tags:
            query = query.filter(model.DBrule.tags.like(f"%{tag}%"))

    if findings_filter.start_date_time:
        query = query.filter(model.scan.DBscan.timestamp >= findings_filter.start_date_time)
    if findings_filter.end_date_time:
        query = query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_time)

    if findings_filter.event_sent is not None:
        if findings_filter.event_sent:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_not(None))
        else:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_(None))

    if findings_filter.branch_name:
        query = query.filter(model.DBbranch.branch_name == findings_filter.branch_name)
    if findings_filter.repository_name:
        query = query.filter(model.DBrepository.repository_name == findings_filter.repository_name)
    if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
        query = query.filter(model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
    if findings_filter.project_name:
        query = query.filter(model.repository.DBrepository.project_key == findings_filter.project_name)
    if findings_filter.rule_names:
        query = query.filter(model.DBfinding.rule_name.in_(findings_filter.rule_names))
    if findings_filter.finding_statuses:
        query = query.filter(model.finding.DBfinding.status.in_(findings_filter.finding_statuses))

    query = query.order_by(model.finding.DBfinding.id_)
    findings: List[detailed_finding_schema.DetailedFindingRead] = query.offset(skip).limit(limit_val).all()

    return findings


def get_detailed_finding(db_connection: Session, finding_id: int) -> detailed_finding_schema.DetailedFindingRead:
    """
    Retrieve a detailed finding objects matching the provided finding_id
    :param db_connection:
        Session of the database connection
    :param finding_id:
        ID of the finding object for which a DetailedFinding is to be fetched
    :return: DetailedFindingRead
        The output will contain a an object of type DetailedFindingRead,
            or a null object finding was found for the given finding_id
    """
    max_scan_subquery = db_connection.query(model.DBscanFinding.finding_id,
                                            func.max(model.DBscanFinding.scan_id).label("scan_id"))
    max_scan_subquery = max_scan_subquery.group_by(model.DBscanFinding.finding_id).subquery()

    scan_id = model.DBscan.id_.label("scan_id")
    finding = db_connection.query(
        model.DBfinding.id_,
        model.DBfinding.file_path,
        model.DBfinding.line_number,
        model.DBfinding.commit_id,
        model.DBfinding.commit_message,
        model.DBfinding.commit_timestamp,
        model.DBfinding.author,
        model.DBfinding.email,
        model.DBfinding.status,
        model.DBfinding.comment,
        model.DBfinding.rule_name,
        model.DBscan.rule_pack,
        model.DBscan.timestamp,
        scan_id,
        model.DBbranch.branch_name,
        model.DBscan.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepository.project_key,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
    ).join(max_scan_subquery, model.finding.DBfinding.id_ == max_scan_subquery.c.finding_id)\
        .join(model.DBscan,
              model.scan.DBscan.id_ == max_scan_subquery.c.scan_id) \
        .join(model.DBbranch,
              model.branch.DBbranch.id_ == model.scan.DBscan.branch_id) \
        .join(model.DBrepository,
              model.repository.DBrepository.id_ == model.branch.DBbranch.repository_id)\
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)\
        .filter(model.finding.DBfinding.id_ == finding_id).first()

    return finding
