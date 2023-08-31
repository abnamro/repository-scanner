# pylint: disable=R0916,R0912,C0121,not-callable
# Standard Library
import logging
from datetime import datetime, timedelta

# Third Party
from sqlalchemy import and_, extract, func, or_
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.time_period import TimePeriod

logger = logging.getLogger(__name__)


def create_audit(db_connection: Session, finding_id: int, auditor: str,
                 status: FindingStatus, comment: str = "") -> model.DBaudit:
    """
        Audit finding, updating the status and comment
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :param auditor:
        identifier of the person performing the audit action
    :param status:
        audit status to set, type FindingStatus
    :param comment:
        audit comment to set
    :return: DBaudit
        The output will contain the audit that was created
    """
    db_audit = model.audit.DBaudit(
        finding_id=finding_id,
        auditor=auditor,
        status=status,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db_connection.add(db_audit)
    db_connection.commit()
    db_connection.refresh(db_audit)

    return db_audit


def get_finding_audits(db_connection: Session, finding_id: int, skip: int = 0,
                       limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> [model.DBaudit]:
    """
        Get Audit entries for finding
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBaudit]
        The output will contain the list of audit items for the given finding
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.DBaudit).filter(model.DBaudit.finding_id == finding_id)
    query = query.order_by(model.DBaudit.id_.desc()).offset(skip).limit(limit_val)
    finding_audits = query.all()
    return finding_audits


def get_finding_audits_count(db_connection: Session, finding_id: int) -> int:
    """
        Get count of Audit entries for finding
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :return: total_count
        count of audit entries
    """
    total_count = db_connection.query(func.count(model.DBaudit.id_)) \
        .filter(model.DBaudit.finding_id == finding_id).scalar()
    return total_count


def get_audit_count_by_auditor_over_time(db_connection: Session, weeks: int = 13) -> list[Row]:
    """
        Retrieve count audits by auditor over time for given weeks
    :param db_connection:
        Session of the database connection
    :param weeks:
        optional, filter on last n weeks, default 13
    :return: count_over_time
        list of rows containing audit count over time per week
    """
    last_nth_week_date_time = datetime.utcnow() - timedelta(weeks=weeks)

    query = db_connection.query(extract('year', model.DBaudit.timestamp).label("year"),
                                extract('week', model.DBaudit.timestamp).label("week"),
                                model.DBaudit.auditor,
                                func.count(model.DBaudit.id_).label("audit_count")) \
        .filter(or_(extract('year', model.DBaudit.timestamp) > extract('year', last_nth_week_date_time),
                and_(extract('year', model.DBaudit.timestamp) == extract('year', last_nth_week_date_time),
                extract('week', model.DBaudit.timestamp) >= extract('week', last_nth_week_date_time)))) \
        .group_by(extract('year', model.DBaudit.timestamp).label("year"),
                  extract('week', model.DBaudit.timestamp).label("week"),
                  model.DBaudit.auditor) \
        .order_by(extract('year', model.DBaudit.timestamp).label("year"),
                  extract('week', model.DBaudit.timestamp).label("week"),
                  model.DBaudit.auditor)
    finding_audits = query.all()

    return finding_audits


def get_personal_audit_count(db_connection: Session, auditor: str, time_period: TimePeriod) -> int:
    """
        Get count of Audit entries for finding
    :param db_connection:
        Session of the database connection
    :param auditor:
        id of the auditor
    :param time_period:
        period for which to retrieve the audit counts
    :return: total_count
        count of audit entries
    """
    date_today = datetime.utcnow()

    total_count = db_connection.query(func.count(model.DBaudit.id_))

    if time_period in (time_period.DAY, time_period.MONTH, time_period.YEAR):
        total_count = total_count.filter(extract('year', model.DBaudit.timestamp) == extract('year', date_today))

        if time_period in (time_period.DAY, time_period.MONTH):
            total_count = total_count.filter(extract('month', model.DBaudit.timestamp) == extract('month', date_today))

            if time_period == time_period.DAY:
                total_count = total_count.filter(extract('day', model.DBaudit.timestamp) == extract('day', date_today))

    if time_period in (time_period.WEEK, time_period.LAST_WEEK):
        date_last_week = datetime.utcnow() - timedelta(weeks=1)
        date_week = date_last_week if time_period == time_period.LAST_WEEK else date_today
        total_count = total_count.filter(extract('year', model.DBaudit.timestamp) == extract('year', date_week))
        total_count = total_count.filter(extract('week', model.DBaudit.timestamp) == extract('week', date_week))

    total_count = total_count.filter(model.DBaudit.auditor == auditor).scalar()
    return total_count
