# pylint: disable=E1101,not-callable
# Standard Library
from typing import List

# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.crud import finding as finding_crud
from resc_backend.resc_web_service.crud import repository as repository_crud
from resc_backend.resc_web_service.crud import scan as scan_crud
from resc_backend.resc_web_service.crud import scan_finding as scan_finding_crud
from resc_backend.resc_web_service.schema import vcs_instance as vcs_instance_schema
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


def get_vcs_instance(db_connection: Session, vcs_instance_id: int):
    vcs_instance = db_connection.query(
        model.DBVcsInstance).filter(model.vcs_instance.DBVcsInstance.id_ == vcs_instance_id).first()
    return vcs_instance


def get_vcs_instances(db_connection: Session, skip: int = 0, limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT,
                      vcs_provider_type: VCSProviders = None, vcs_instance_name: str = None) \
        -> List[model.DBVcsInstance]:
    """
        Retrieve all vcs_instances records
    :param db_connection:
        Session of the database connection
    :param vcs_provider_type:
        optional filtering by VCS Provider type
    :param vcs_instance_name:
        optional filtering by VCS Provider name
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBVcsInstance]
        List of DBVcsInstance objects
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.DBVcsInstance)

    if vcs_provider_type:
        query = query.filter(model.DBVcsInstance.provider_type == vcs_provider_type)

    if vcs_instance_name:
        query = query.filter(model.DBVcsInstance.name == vcs_instance_name)

    vcs_instances = query.order_by(model.vcs_instance.DBVcsInstance.id_).offset(skip).limit(limit_val).all()
    return vcs_instances


def get_vcs_instances_count(db_connection: Session,
                            vcs_provider_type: VCSProviders = None, vcs_instance_name: str = None) -> int:
    """
        Retrieve count of vcs_instances records optionally filtered by VCS provider
    :param db_connection:
        Session of the database connection
    :param vcs_provider_type:
        optional vcs_provider_type filtering the vcs provider type for which to count vcs instances
    :param vcs_instance_name:
        optional vcs_instance_name filtering the vcs provider name for which to count vcs instances
    :return: total_count
        count of vcs instances
    """
    query = db_connection.query(func.count(model.DBVcsInstance.id_))

    if vcs_provider_type:
        query = query.filter(model.DBVcsInstance.provider_type == vcs_provider_type)

    if vcs_instance_name:
        query = query.filter(model.DBVcsInstance.name == vcs_instance_name)

    total_count = query.scalar()
    return total_count


def update_vcs_instance(
        db_connection: Session,
        vcs_instance_id: int,
        vcs_instance: vcs_instance_schema.VCSInstanceCreate) -> model.DBVcsInstance:
    db_vcs_instance: model.DBVcsInstance = \
        db_connection.query(model.DBVcsInstance).filter_by(id_=vcs_instance_id).first()
    db_vcs_instance.name = vcs_instance.name
    db_vcs_instance.provider_type = vcs_instance.provider_type
    db_vcs_instance.port = vcs_instance.port
    db_vcs_instance.scheme = vcs_instance.scheme
    db_vcs_instance.organization = vcs_instance.organization
    db_vcs_instance.hostname = vcs_instance.hostname
    db_vcs_instance.scope = ",".join(vcs_instance.scope)
    db_vcs_instance.exceptions = ",".join(vcs_instance.exceptions)

    db_connection.commit()
    db_connection.refresh(db_vcs_instance)
    return db_vcs_instance


def create_vcs_instance(db_connection: Session, vcs_instance: vcs_instance_schema.VCSInstanceCreate) \
        -> model.DBVcsInstance:
    db_vcs_instance = model.vcs_instance.DBVcsInstance(
        name=vcs_instance.name,
        provider_type=vcs_instance.provider_type,
        port=vcs_instance.port,
        scheme=vcs_instance.scheme,
        organization=vcs_instance.organization,
        hostname=vcs_instance.hostname,
        scope=",".join(vcs_instance.scope),
        exceptions=",".join(vcs_instance.exceptions)
    )
    db_connection.add(db_vcs_instance)
    db_connection.commit()
    db_connection.refresh(db_vcs_instance)
    return db_vcs_instance


def create_vcs_instance_if_not_exists(db_connection: Session, vcs_instance: vcs_instance_schema.VCSInstanceCreate):
    # Query the database to see if the vcs_instance object exists based on the unique constraint parameters
    db_select_vcs_instance = db_connection.query(model.DBVcsInstance) \
        .filter(model.DBVcsInstance.provider_type == vcs_instance.provider_type,
                model.DBVcsInstance.scheme == vcs_instance.scheme,
                model.DBVcsInstance.hostname == vcs_instance.hostname,
                model.DBVcsInstance.port == vcs_instance.port,
                model.DBVcsInstance.organization == vcs_instance.organization).first()
    if db_select_vcs_instance is not None:
        return db_select_vcs_instance

    # Create non-existing vcs_instance object
    return create_vcs_instance(db_connection, vcs_instance)


def delete_vcs_instance(db_connection: Session, vcs_instance_id: int, delete_related: bool = False):
    """
        Delete a vcs instance object
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the vcs instance to be deleted
    :param delete_related:
        if related records need to be deleted
    """
    if delete_related:
        scan_finding_crud.delete_scan_finding_by_vcs_instance_id(db_connection, vcs_instance_id=vcs_instance_id)
        finding_crud.delete_findings_by_vcs_instance_id(db_connection, vcs_instance_id=vcs_instance_id)
        scan_crud.delete_scans_by_vcs_instance_id(db_connection, vcs_instance_id=vcs_instance_id)
        repository_crud.delete_repositories_by_vcs_instance_id(db_connection, vcs_instance_id=vcs_instance_id)
    db_vcs_instance = db_connection.query(model.DBVcsInstance).filter_by(id_=vcs_instance_id).first()
    db_connection.delete(db_vcs_instance)
    db_connection.commit()
