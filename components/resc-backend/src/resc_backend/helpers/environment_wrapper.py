# Standard Library
import os
from dataclasses import dataclass


@dataclass
class EnvironmentVariable:
    key_name: str
    help_text: str
    default: str = ""
    required: bool = False


def validate_environment(env_variables):
    missing = []
    values = {}
    for env_variable in env_variables:
        value = os.environ.get(env_variable.key_name, env_variable.default)
        if not value and env_variable.required:
            missing.append(f"{env_variable.key_name}: {env_variable.help_text}")
        else:
            values[env_variable.key_name] = value

    if missing:
        raise EnvironmentError(f"The following env variables need to be set: {', '.join(missing)}")
    return values
