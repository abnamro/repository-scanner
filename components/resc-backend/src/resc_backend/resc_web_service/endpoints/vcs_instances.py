# Standard Library
import logging
from typing import Optional

# Third Party
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, RWS_ROUTE_VCS, VCS_TAG
from resc_backend.db.connection import Session
from resc_backend.resc_web_service.crud import vcs_instance as vcs_instance_crud
from resc_backend.resc_web_service.dependencies import get_db_connection
from resc_backend.resc_web_service.schema import vcs_instance as vcs_instance_schema
from resc_backend.resc_web_service.schema.pagination_model import PaginationModel
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

router = APIRouter(prefix=f"{RWS_ROUTE_VCS}", tags=[VCS_TAG])
logger = logging.getLogger(__name__)


@router.post("", response_model=vcs_instance_schema.VCSInstanceRead, status_code=status.HTTP_201_CREATED)
def create_vcs_instance(vcs_instance: vcs_instance_schema.VCSInstanceCreate,
                        db_connection: Session = Depends(get_db_connection)) \
        -> vcs_instance_schema.VCSInstanceRead:
    """
        Create new VCS instance object
    :param db_connection:
        Session of the database connection
    :param vcs_instance:
        VCSInstanceCreate type object of the VCS Instance to create
    :return: VCSInstanceRead
        The output will contain a VCSInstanceRead type object if the creation was successful
    """
    try:
        created_vcs_instance = vcs_instance_crud.create_vcs_instance_if_not_exists(db_connection=db_connection,
                                                                                   vcs_instance=vcs_instance)
    except IntegrityError as err:
        logger.debug(f"Error creating new vcs_instance object: {err}")
        raise HTTPException(status_code=400, detail="Error creating new vcs_instance object") from err
    vcs_instance = vcs_instance_schema.VCSInstanceRead.create_from_db_vcs_instance(created_vcs_instance)
    return vcs_instance


@router.get("/{vcs_instance_id}", response_model=vcs_instance_schema.VCSInstanceRead, status_code=status.HTTP_200_OK)
def read_vcs_instance(vcs_instance_id: int, db_connection: Session = Depends(get_db_connection)) \
        -> vcs_instance_schema.VCSInstanceRead:
    """
        Get a VCS instance object based on the provided id
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the VCS instance to get
    :return: VCSInstanceRead
        The output will contain a VCSInstanceRead type object from the requested id
    """
    db_vcs_instance = vcs_instance_crud.get_vcs_instance(db_connection, vcs_instance_id=vcs_instance_id)
    if db_vcs_instance is None:
        raise HTTPException(status_code=404, detail="VCS Instance not found")
    vcs_instance = vcs_instance_schema.VCSInstanceRead.create_from_db_vcs_instance(db_vcs_instance)
    return vcs_instance


@router.get("", response_model=PaginationModel[vcs_instance_schema.VCSInstanceRead], status_code=status.HTTP_200_OK)
def get_all_vcs_instances(skip: int = Query(default=0, ge=0),
                          limit: int = Query(default=DEFAULT_RECORDS_PER_PAGE_LIMIT, ge=1),
                          vcs_provider_type: Optional[VCSProviders] = Query(None),
                          vcs_instance_name: Optional[str] = Query(None),
                          db_connection: Session = Depends(get_db_connection)) \
        -> PaginationModel[vcs_instance_schema.VCSInstanceRead]:
    """
        Retrieve all VCS instance objects paginated
    :param db_connection:
        Session of the database connection
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :param vcs_provider_type:
        Optional filter for the provider type
    :param vcs_instance_name:
        Optional filter for the provider name
    :return: [VCSInstanceRead]
        The output will contain a PaginationModel containing the list of VCSInstanceRead type objects,
        or an empty list if no VCS instance was found
    """
    db_vcs_instances = vcs_instance_crud.get_vcs_instances(db_connection, skip=skip, limit=limit,
                                                           vcs_provider_type=vcs_provider_type,
                                                           vcs_instance_name=vcs_instance_name)
    vcs_instances = []
    for db_vcs_instance in db_vcs_instances:
        vcs_instances.append(vcs_instance_schema.VCSInstanceRead.create_from_db_vcs_instance(db_vcs_instance))

    total_vcs_instances = vcs_instance_crud.get_vcs_instances_count(db_connection, vcs_provider_type=vcs_provider_type,
                                                                    vcs_instance_name=vcs_instance_name)

    return PaginationModel[vcs_instance_schema.VCSInstanceRead](data=vcs_instances, total=total_vcs_instances,
                                                                limit=limit, skip=skip)


@router.put("/{vcs_instance_id}", response_model=vcs_instance_schema.VCSInstanceRead, status_code=status.HTTP_200_OK)
def update_vcs_instance(vcs_instance_id: int, vcs_instance: vcs_instance_schema.VCSInstanceCreate,
                        db_connection: Session = Depends(get_db_connection)) \
        -> vcs_instance_schema.VCSInstanceRead:
    """
        Update a VCS instance object
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the VCS instance to update
    :param vcs_instance:
        VCSInstanceCreate type object of the VCS Instance to update the values to
    :return: VCSInstanceRead
        The output will contain a VCSInstanceRead type object with the new properties
    """
    db_vcs_instance = vcs_instance_crud.get_vcs_instance(db_connection, vcs_instance_id=vcs_instance_id)
    if db_vcs_instance is None:
        raise HTTPException(status_code=404, detail="VCS instance not found")
    db_vcs_instance = vcs_instance_crud.update_vcs_instance(db_connection=db_connection,
                                                            vcs_instance_id=vcs_instance_id, vcs_instance=vcs_instance)
    vcs_instance = vcs_instance_schema.VCSInstanceRead.create_from_db_vcs_instance(db_vcs_instance)
    return vcs_instance


@router.delete("/{vcs_instance_id}",
               status_code=status.HTTP_200_OK)
def delete_vcs_instance(vcs_instance_id: int, db_connection: Session = Depends(get_db_connection)):
    """
        Delete a VCS instance object
    :param db_connection:
        Session of the database connection
    :param vcs_instance_id:
        id of the VCS instance to delete
    :return:
        The output will contain a success or error message based on the success of the deletion
    """
    db_vcs_instance = vcs_instance_crud.get_vcs_instance(db_connection, vcs_instance_id=vcs_instance_id)
    if db_vcs_instance is None:
        raise HTTPException(status_code=404, detail="VCS instance not found")
    vcs_instance_crud.delete_vcs_instance(db_connection, vcs_instance_id=vcs_instance_id, delete_related=True)
    return {"ok": True}
