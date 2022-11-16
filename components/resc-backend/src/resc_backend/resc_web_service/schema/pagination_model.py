# Standard Library
from typing import Generic, TypeVar

# Third Party
# pylint: disable=no-name-in-module
from pydantic import BaseModel, conint, conlist
from pydantic.generics import GenericModel

# First Party
from resc_backend.constants import MAX_RECORDS_PER_PAGE_LIMIT

Model = TypeVar("Model", bound=BaseModel)


class PaginationModel(GenericModel, Generic[Model]):
    """
        Generic encapsulation class for paginated endpoints to standardize output of the API
        example creation, PaginationModel[FindingRead](data=db_findings, total=total, limit=limit, skip=skip)
    :param Generic[Model]:
        Type of the object in the data list
    """
    # data: List[Model]
    data: conlist(item_type=Model, min_items=None, max_items=MAX_RECORDS_PER_PAGE_LIMIT)
    total: conint(gt=-1)
    limit: conint(gt=-1)
    skip: conint(gt=-1)

    class Config:
        orm_mode = True
