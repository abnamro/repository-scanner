# pylint: disable=R0912,C0121,R0915
# Standard Library
from typing import List

# Third Party
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.filters import FindingsFilter
from resc_backend.resc_web_service.schema import detailed_finding as detailed_finding_schema
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.scan_type import ScanType


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
    max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                 func.max(model.DBscan.id_).label("latest_base_scan_id"))
    max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
    if findings_filter.rule_pack_versions:
        max_base_scan_subquery = max_base_scan_subquery.filter(
            model.DBscan.rule_pack.in_(findings_filter.rule_pack_versions))
    max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

    # subquery to select latest audit ids of findings
    max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                             func.max(model.DBaudit.id_).label("audit_id")) \
        .group_by(model.DBaudit.finding_id).subquery()

    rule_tag_subquery = db_connection.query(model.DBruleTag.rule_id) \
        .join(model.DBtag, model.DBruleTag.tag_id == model.DBtag.id_)
    if findings_filter.rule_tags:
        rule_tag_subquery = rule_tag_subquery.filter(model.DBtag.name.in_(findings_filter.rule_tags))
    if findings_filter.rule_pack_versions or findings_filter.rule_names:
        rule_tag_subquery = rule_tag_subquery.join(model.DBrule, model.DBrule.id_ == model.DBruleTag.rule_id)
        if findings_filter.rule_pack_versions:
            rule_tag_subquery = rule_tag_subquery.filter(model.DBrule.rule_pack.in_(findings_filter.rule_pack_versions))
        if findings_filter.rule_names:
            rule_tag_subquery = rule_tag_subquery.filter(model.DBrule.rule_name.in_(findings_filter.rule_names))
    rule_tag_subquery = rule_tag_subquery.group_by(model.DBruleTag.rule_id).subquery()

    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit

    query = db_connection.query(
        model.DBfinding.id_,
        model.DBfinding.file_path,
        model.DBfinding.line_number,
        model.DBfinding.column_start,
        model.DBfinding.column_end,
        model.DBfinding.commit_id,
        model.DBfinding.commit_message,
        model.DBfinding.commit_timestamp,
        model.DBfinding.author,
        model.DBfinding.email,
        model.DBaudit.status,
        model.DBaudit.comment,
        model.DBfinding.rule_name,
        model.DBscan.rule_pack,
        model.DBfinding.event_sent_on,
        model.DBscan.timestamp,
        model.DBscan.id_.label("scan_id"),
        model.DBscan.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepository.project_key,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
    )
    query = query.join(model.DBscanFinding, model.DBfinding.id_ == model.DBscanFinding.finding_id)
    if findings_filter.scan_ids:
        query = query.join(model.DBscan, and_(model.DBscanFinding.scan_id == model.DBscan.id_,
                                              model.DBscan.id_.in_(findings_filter.scan_ids)))
    else:
        query = query.join(max_base_scan_subquery,
                           model.DBfinding.repository_id == max_base_scan_subquery.c.repository_id)
        query = query.join(model.DBscan, and_(model.DBscanFinding.scan_id == model.DBscan.id_,
                                              model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))
    query = query.join(model.DBrepository,
                       model.repository.DBrepository.id_ == model.finding.DBfinding.repository_id) \
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
    query = query.join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
                       isouter=True)
    query = query.join(model.DBaudit, and_(model.audit.DBaudit.finding_id == model.finding.DBfinding.id_,
                                           model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id),
                       isouter=True)

    if findings_filter.rule_tags:
        query = query.join(model.DBrule, and_(model.DBrule.rule_name == model.DBfinding.rule_name,
                                              model.DBrule.rule_pack == model.DBscan.rule_pack))
        query = query.join(rule_tag_subquery, model.DBrule.id_ == rule_tag_subquery.c.rule_id)

    if findings_filter.rule_pack_versions:
        query = query.filter(model.DBscan.rule_pack.in_(findings_filter.rule_pack_versions))
    if findings_filter.start_date_time:
        query = query.filter(model.scan.DBscan.timestamp >= findings_filter.start_date_time)
    if findings_filter.end_date_time:
        query = query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_time)

    if findings_filter.event_sent is not None:
        if findings_filter.event_sent:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_not(None))
        else:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_(None))

    if findings_filter.repository_name:
        query = query.filter(model.DBrepository.repository_name == findings_filter.repository_name)
    if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
        query = query.filter(model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
    if findings_filter.project_name:
        query = query.filter(model.repository.DBrepository.project_key == findings_filter.project_name)
    if findings_filter.rule_names:
        query = query.filter(model.DBfinding.rule_name.in_(findings_filter.rule_names))
    if findings_filter.finding_statuses:
        if FindingStatus.NOT_ANALYZED in findings_filter.finding_statuses:
            query = query.filter(or_(model.DBaudit.status.in_(findings_filter.finding_statuses),
                                     model.DBaudit.status == None))  # noqa: E711
        else:
            query = query.filter(model.DBaudit.status.in_(findings_filter.finding_statuses))

    query = query.order_by(model.finding.DBfinding.id_)
    findings: List[detailed_finding_schema.DetailedFindingRead] = query.offset(skip).limit(limit_val).all()

    return findings


def get_detailed_findings_count(db_connection: Session, findings_filter: FindingsFilter) -> int:
    """
    Retrieve count of detailed findings objects matching the provided FindingsFilter
    :param findings_filter:
        Object of type FindingsFilter, only DetailedFindingRead objects matching the attributes in this filter will be
            fetched
    :param db_connection:
        Session of the database connection
    :return: total_count
        count of findings
    """
    # subquery to select latest audit ids of findings
    max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                             func.max(model.DBaudit.id_).label("audit_id")) \
        .group_by(model.DBaudit.finding_id).subquery()

    max_base_scan_subquery = db_connection.query(model.DBscan.repository_id,
                                                 func.max(model.DBscan.id_).label("latest_base_scan_id"))
    max_base_scan_subquery = max_base_scan_subquery.filter(model.DBscan.scan_type == ScanType.BASE)
    if findings_filter.rule_pack_versions:
        max_base_scan_subquery = max_base_scan_subquery.filter(
            model.DBscan.rule_pack.in_(findings_filter.rule_pack_versions))
    max_base_scan_subquery = max_base_scan_subquery.group_by(model.DBscan.repository_id).subquery()

    rule_tag_subquery = db_connection.query(model.DBruleTag.rule_id) \
        .join(model.DBtag, model.DBruleTag.tag_id == model.DBtag.id_)
    if findings_filter.rule_tags:
        rule_tag_subquery = rule_tag_subquery.filter(model.DBtag.name.in_(findings_filter.rule_tags))
    if findings_filter.rule_pack_versions or findings_filter.rule_names:
        rule_tag_subquery = rule_tag_subquery.join(model.DBrule, model.DBrule.id_ == model.DBruleTag.rule_id)
        if findings_filter.rule_pack_versions:
            rule_tag_subquery = rule_tag_subquery.filter(model.DBrule.rule_pack.in_(findings_filter.rule_pack_versions))
        if findings_filter.rule_names:
            rule_tag_subquery = rule_tag_subquery.filter(model.DBrule.rule_name.in_(findings_filter.rule_names))
    rule_tag_subquery = rule_tag_subquery.group_by(model.DBruleTag.rule_id).subquery()

    query = db_connection.query(func.count(model.DBfinding.id_))

    query = query.join(model.DBscanFinding, model.DBfinding.id_ == model.DBscanFinding.finding_id)
    if findings_filter.scan_ids:
        query = query.join(model.DBscan, and_(model.DBscanFinding.scan_id == model.DBscan.id_,
                                              model.DBscan.id_.in_(findings_filter.scan_ids)))
    else:
        query = query.join(max_base_scan_subquery,
                           model.DBfinding.repository_id == max_base_scan_subquery.c.repository_id)
        query = query.join(model.DBscan, and_(model.DBscanFinding.scan_id == model.DBscan.id_,
                                              model.DBscan.id_ >= max_base_scan_subquery.c.latest_base_scan_id))

    query = query.join(model.DBrepository,
                       model.repository.DBrepository.id_ == model.finding.DBfinding.repository_id) \
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance)
    query = query.join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
                       isouter=True)
    query = query.join(model.DBaudit, and_(model.audit.DBaudit.finding_id == model.finding.DBfinding.id_,
                                           model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id),
                       isouter=True)

    if findings_filter.rule_tags:
        query = query.join(model.DBrule, and_(model.DBrule.rule_name == model.DBfinding.rule_name,
                                              model.DBrule.rule_pack == model.DBscan.rule_pack))
        query = query.join(rule_tag_subquery, model.DBrule.id_ == rule_tag_subquery.c.rule_id)

    if findings_filter.rule_pack_versions:
        query = query.filter(model.DBscan.rule_pack.in_(findings_filter.rule_pack_versions))
    if findings_filter.start_date_time:
        query = query.filter(model.scan.DBscan.timestamp >= findings_filter.start_date_time)
    if findings_filter.end_date_time:
        query = query.filter(model.scan.DBscan.timestamp <= findings_filter.end_date_time)

    if findings_filter.event_sent is not None:
        if findings_filter.event_sent:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_not(None))
        else:
            query = query.filter(model.finding.DBfinding.event_sent_on.is_(None))

    if findings_filter.repository_name:
        query = query.filter(model.DBrepository.repository_name == findings_filter.repository_name)
    if findings_filter.vcs_providers and findings_filter.vcs_providers is not None:
        query = query.filter(model.vcs_instance.DBVcsInstance.provider_type.in_(findings_filter.vcs_providers))
    if findings_filter.project_name:
        query = query.filter(model.repository.DBrepository.project_key == findings_filter.project_name)
    if findings_filter.rule_names:
        query = query.filter(model.DBfinding.rule_name.in_(findings_filter.rule_names))
    if findings_filter.finding_statuses:
        if FindingStatus.NOT_ANALYZED in findings_filter.finding_statuses:
            query = query.filter(or_(model.DBaudit.status.in_(findings_filter.finding_statuses),
                                     model.DBaudit.status == None))  # noqa: E711
        else:
            query = query.filter(model.DBaudit.status.in_(findings_filter.finding_statuses))

    findings_count = query.scalar()
    return findings_count


def get_detailed_finding(db_connection: Session, finding_id: int) -> detailed_finding_schema.DetailedFindingRead:
    """
    Retrieve a detailed finding objects matching the provided finding_id
    :param db_connection:
        Session of the database connection
    :param finding_id:
        ID of the finding object for which a DetailedFinding is to be fetched
    :return: DetailedFindingRead
        The output will contain an object of type DetailedFindingRead,
            or a null object finding was found for the given finding_id
    """
    max_scan_subquery = db_connection.query(model.DBscanFinding.finding_id,
                                            func.max(model.DBscanFinding.scan_id).label("scan_id"))
    max_scan_subquery = max_scan_subquery.group_by(model.DBscanFinding.finding_id).subquery()

    # subquery to select latest audit ids of findings
    max_audit_subquery = db_connection.query(model.DBaudit.finding_id,
                                             func.max(model.DBaudit.id_).label("audit_id")) \
        .group_by(model.DBaudit.finding_id).subquery()

    scan_id = model.DBscan.id_.label("scan_id")
    query = db_connection.query(
        model.DBfinding.id_,
        model.DBfinding.file_path,
        model.DBfinding.line_number,
        model.DBfinding.column_start,
        model.DBfinding.column_end,
        model.DBfinding.commit_id,
        model.DBfinding.commit_message,
        model.DBfinding.commit_timestamp,
        model.DBfinding.author,
        model.DBfinding.email,
        model.DBaudit.status,
        model.DBaudit.comment,
        model.DBfinding.rule_name,
        model.DBscan.rule_pack,
        model.DBscan.timestamp,
        scan_id,
        model.DBscan.last_scanned_commit,
        model.DBVcsInstance.provider_type.label("vcs_provider"),
        model.DBrepository.project_key,
        model.DBrepository.repository_name,
        model.DBrepository.repository_url,
    ).join(max_scan_subquery, model.finding.DBfinding.id_ == max_scan_subquery.c.finding_id) \
        .join(model.DBscan,
              model.scan.DBscan.id_ == max_scan_subquery.c.scan_id) \
        .join(model.DBrepository,
              model.repository.DBrepository.id_ == model.scan.DBscan.repository_id) \
        .join(model.DBVcsInstance,
              model.vcs_instance.DBVcsInstance.id_ == model.repository.DBrepository.vcs_instance) \
        .join(max_audit_subquery, max_audit_subquery.c.finding_id == model.finding.DBfinding.id_,
              isouter=True) \
        .join(model.DBaudit, and_(model.audit.DBaudit.finding_id == model.finding.DBfinding.id_,
                                  model.audit.DBaudit.id_ == max_audit_subquery.c.audit_id),
              isouter=True) \
        .filter(model.finding.DBfinding.id_ == finding_id)
    finding = query.first()
    return finding
