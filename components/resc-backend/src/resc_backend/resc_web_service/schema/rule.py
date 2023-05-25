# pylint: disable=no-name-in-module
# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr


class RuleBase(BaseModel):
    rule_name: constr(min_length=1, max_length=400)
    description: Optional[constr(max_length=2000)] = None
    entropy: Optional[float] = None
    secret_group: Optional[int] = None
    regex: Optional[str] = None
    path: Optional[str] = None
    keywords: Optional[str] = None


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
