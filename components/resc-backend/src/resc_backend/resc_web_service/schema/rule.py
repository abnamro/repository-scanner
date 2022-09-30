# pylint: disable=no-name-in-module
# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr


class RuleBase(BaseModel):
    rule_name: constr(min_length=1, max_length=400)
    description: constr(min_length=1, max_length=400)
    tags: Optional[constr(max_length=400)] = None
    entropy: Optional[float] = None
    secret_group: Optional[int] = None
    regex: Optional[constr(max_length=1000)] = None
    path: Optional[constr(max_length=1000)] = None
    keywords: Optional[constr(max_length=400)] = None


class RuleCreate(RuleBase):
    rule_pack: constr(regex=r'^(\d+\.)?(\d+\.)?(\*|\d+)$')
    allow_list: Optional[conint(gt=0)] = None

    @classmethod
    def create_from_base_class(cls, base_object: RuleBase, rule_pack: str, allow_list=int):
        return cls(**(dict(base_object)), rule_pack=rule_pack, allow_list=allow_list)


class Rule(RuleBase):
    pass


class RuleRead(RuleCreate):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
