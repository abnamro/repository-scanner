# Standard Library
from typing import Generic, TypeVar

# Third Party
# pylint: disable=no-name-in-module
from pydantic import BaseModel, conint, conlist
from pydantic.generics import GenericModel

Model = TypeVar("Model", bound=BaseModel)


class PaginationModel(GenericModel, Generic[Model]):
    """
        Generic encapsulation class for paginated endpoints to standardize output of the API
        example creation, PaginationModel[FindingRead](data=db_findings, total=total, limit=limit, skip=skip)
    :param Generic[Model]:
        Type of the object in the data list
    """
    # data: List[Model]
    data: conlist(item_type=Model, min_items=None, max_items=500)
    total: conint(gt=-1)
    limit: conint(gt=-1)
    skip: conint(gt=-1)

    class Config:
        orm_mode = True
