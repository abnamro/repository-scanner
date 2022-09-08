# pylint: disable=R0912
# Standard Library
from typing import List

# Third Party
from sqlalchemy.orm import Session

# First Party
from repository_scanner_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from repository_scanner_backend.db import model
from repository_scanner_backend.resc_web_service.filters import FindingsFilter
from repository_scanner_backend.resc_web_service.schema import detailed_finding as detailed_finding_schema


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

    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    scan_id = model.DBscanFinding.scan_id.label("scan_id")
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
        model.DBrule.rule_name,
        model.DBscan.rule_pack,
        model.DBfinding.event_sent_on,
        model.DBscan.timestamp,
        scan_id,
        model.DBbranchInfo.branch_name,
        model.DBbranchInfo.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepositoryInfo.project_key,
        model.DBrepositoryInfo.repository_name,
        model.DBrepositoryInfo.repository_url,
    ).join(model.DBrule, model.DBfinding.rule_name == model.DBrule.rule_name)\
        .join(model.scan_finding.DBscanFinding,
              model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
        .join(model.DBscan,
              model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
        .join(model.DBbranchInfo,
              model.branch_info.DBbranchInfo.id_ == model.finding.DBfinding.branch_info_id) \
        .join(model.DBrepositoryInfo,
              model.repository_info.DBrepositoryInfo.id_ == model.branch_info.DBbranchInfo.repository_info_id)\
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance) \
        .order_by(model.finding.DBfinding.id_)

    if findings_filter.start_date_range:
        query = query.filter(model.scan.DBscan.timestamp >= findings_filter.start_date_range)
    if findings_filter.end_date_range:
        query = query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_range)

    if findings_filter.event_sent is not None:
        if findings_filter.event_sent:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_not(None))
        else:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_(None))

    if findings_filter.branch_name:
        query = query.filter(model.DBbranchInfo.branch_name == findings_filter.branch_name)
    if findings_filter.repository_name:
        query = query.filter(model.DBrepositoryInfo.repository_name == findings_filter.repository_name)
    if findings_filter.scan_ids:
        if len(findings_filter.scan_ids) == 1:
            query = query.filter(model.scan_finding.DBscanFinding.scan_id == findings_filter.scan_ids[0])
        if len(findings_filter.scan_ids) >= 2:
            query = query.filter(model.scan_finding.DBscanFinding.scan_id.in_(findings_filter.scan_ids))
    if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
        query = query.filter(model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
    if findings_filter.project_name:
        query = query.filter(model.repository_info.DBrepositoryInfo.project_key == findings_filter.project_name)
    if findings_filter.rule_names:
        query = query.filter(model.DBrule.rule_name.in_(findings_filter.rule_names))
    if findings_filter.finding_statuses:
        query = query.filter(model.finding.DBfinding.status.in_(findings_filter.finding_statuses))
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
        model.DBrule.rule_name,
        model.DBscan.rule_pack,
        model.DBscan.timestamp,
        scan_id,
        model.DBbranchInfo.branch_name,
        model.DBbranchInfo.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepositoryInfo.project_key,
        model.DBrepositoryInfo.repository_name,
        model.DBrepositoryInfo.repository_url,
    ).join(model.DBrule, model.DBfinding.rule_id == model.DBrule.id_) \
        .join(model.DBscanFinding,
              model.scan_finding.DBscanFinding.finding_id == model.finding.DBfinding.id_) \
        .join(model.DBscan,
              model.scan.DBscan.id_ == model.scan_finding.DBscanFinding.scan_id) \
        .join(model.DBbranchInfo,
              model.branch_info.DBbranchInfo.id_ == model.scan.DBscan.branch_info_id) \
        .join(model.DBrepositoryInfo,
              model.repository_info.DBrepositoryInfo.id_ == model.branch_info.DBbranchInfo.repository_info_id)\
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository_info.DBrepositoryInfo.vcs_instance)\
        .filter(model.finding.DBfinding.id_ == finding_id).first()

    return finding
