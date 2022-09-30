# pylint: disable=no-name-in-module
# Standard Library
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr

RULE_PACK_VERSION_REGEX = r"^\d+(?:\.\d+){2}$"


class RulePackBase(BaseModel):
    version: constr(regex=RULE_PACK_VERSION_REGEX)
    active: bool = False
    global_allow_list: Optional[conint(gt=0)]


class RulePackCreate(RulePackBase):
    version: constr(regex=RULE_PACK_VERSION_REGEX)
    global_allow_list: Optional[conint(gt=0)]

    @classmethod
    def create_from_base_class(cls, base_object: RulePackBase, global_allow_list: int):
        return cls(**(dict(base_object)), global_allow_list=global_allow_list)


class RulePack(RulePackBase):
    pass


class RulePackRead(RulePackBase):
    version: constr(regex=RULE_PACK_VERSION_REGEX)

    class Config:
        orm_mode = True
