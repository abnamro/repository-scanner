# Standard Library
import logging.config
import sys
from distutils.sysconfig import get_python_lib
from os import path
from typing import Dict, List

# Third Party
from celery import Celery

# First Party
from vcs_scraper.model import VCSInstance
from vcs_scraper.vcs_instances_parser import parse_vcs_instances_file

logger = logging.getLogger(__name__)


def get_logging_settings_path():
    if path.isfile(get_python_lib() + "/vcs_scraper"):
        base_dir = get_python_lib() + "/vcs_scraper"
    else:
        base_dir = path.dirname(__file__)

    return base_dir + "/static/logging.ini"


def create_celery_client(queue_name: str, username: str, password: str, service_host: str, virtual_host: str):
    celery_client = Celery(queue_name,
                           broker=f"amqp://{username}:{password}@{service_host}/{virtual_host}")
    celery_client.conf.update({'worker_hijack_root_logger': False})
    celery_client.conf.update({'broker_connection_retry': True})
    celery_client.conf.update({'broker_connection_max_retries': 100})
    return celery_client


def initialise_logs(log_file_path: str, debug: str):
    logging_ini_file = get_logging_settings_path()
    logging.config.fileConfig(logging_ini_file, defaults={'log_file_path': log_file_path},
                              disable_existing_loggers=False)
    logger_config = logging.getLogger('root')
    if int(debug) == 1:
        logger_config.setLevel(logging.DEBUG)
    else:
        logger_config.setLevel(logging.INFO)
    return logger_config


def load_vcs_instances_into_map(file_path: str) -> Dict[str, VCSInstance]:
    vcs_instances: List[VCSInstance] = parse_vcs_instances_file(file_path)
    if not vcs_instances:
        logger.info("Exiting due to issues in VCS Instances definition in file "
                    f"{file_path}")
        sys.exit(-1)
    return {vcs_instance.name: vcs_instance for vcs_instance in vcs_instances}
