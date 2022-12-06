# Standard Library
import logging.config
import sys
from distutils.sysconfig import get_python_lib
from os import path
from typing import Dict, List, Optional

# Third Party
import tomlkit

# First Party
from vcs_scanner.input_parser import parse_vcs_instances_file
from vcs_scanner.model import VCSInstanceRuntime

logger = logging.getLogger(__name__)


def get_logging_settings_path():
    if path.isfile(get_python_lib() + "/vcs_scanner"):
        base_dir = get_python_lib() + "/vcs_scanner"
    else:
        base_dir = path.dirname(__file__)

    return base_dir + "/static/logging.ini"


def generate_logger_config(log_file_path, debug=True):
    """A function to generate the global logger config dictionary

    Arguments:
        log_file_path {string} -- Path where the logs are to be stored

    Keyword Arguments:
        debug {bool} -- Whether the logging level should be set to DEBUG or INFO (default: {True})

    Returns:
        Dict -- A dictionary containing the logger configuration
    """

    logging_level = "DEBUG" if debug else "INFO"
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "generic-log-formatter": {
                "format": "[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": logging_level,
                "class": "logging.StreamHandler",
                "formatter": "generic-log-formatter",
            },
            "file": {
                "level": logging_level,
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "generic-log-formatter",
                "filename": log_file_path,
                "maxBytes": 100 * 1024 * 1024,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": logging_level,
                "propagate": True
            },
        }
    }

    return logging_config


def initialise_logs(log_file_path: str, debug=True):
    logging_ini_file = get_logging_settings_path()
    logging.config.fileConfig(logging_ini_file, defaults={'log_file_path': log_file_path},
                              disable_existing_loggers=False)
    logger_config = logging.getLogger('root')
    if int(debug) == 1:
        logger_config.setLevel(logging.DEBUG)
    else:
        logger_config.setLevel(logging.INFO)
    return logger_config


def load_vcs_instances(file_path: str) -> Dict[str, VCSInstanceRuntime]:
    vcs_instances_list: List[VCSInstanceRuntime] = parse_vcs_instances_file(file_path)
    if not vcs_instances_list:
        logger.critical(f"Exiting due to issues in VCS Instances definition in file {file_path}")
        sys.exit(-1)
    vcs_instances_map: Dict[str, VCSInstanceRuntime] = \
        {vcs_instance.name: vcs_instance for vcs_instance in vcs_instances_list}
    return vcs_instances_map


def get_rule_pack_version_from_file(file_content: str) -> Optional[str]:
    toml_rule_dictionary = tomlkit.loads(file_content)
    rule_pack_version = toml_rule_dictionary["version"] if "version" in toml_rule_dictionary else None
    return rule_pack_version
