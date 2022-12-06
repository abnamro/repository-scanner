# pylint: disable=no-name-in-module
# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr


class RuleAllowListBase(BaseModel):
    description: Optional[constr(max_length=2000)]
    regexes: Optional[str]
    paths: Optional[str]
    commits: Optional[str]
    stop_words: Optional[str]


class RuleAllowListCreate(RuleAllowListBase):

    @classmethod
    def create_from_base_class(cls, base_object: RuleAllowListBase):
        return cls(**(dict(base_object)))


class RuleAllowList(RuleAllowListBase):
    pass


class RuleAllowListRead(RuleAllowListBase):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
