# Standard Library
import logging.config
from os import path
from sysconfig import get_path

# Third Party
import pkg_resources

logger = logging.getLogger(__name__)


def get_logging_settings_path():
    if path.isfile(get_path("purelib") + "/resc"):
        base_dir = get_path("purelib") + "/resc"
    else:
        base_dir = path.dirname(__file__)

    return base_dir + "/static/logging.ini"


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


def get_package_version():
    try:
        version = pkg_resources.get_distribution("resc-backend").version
    except pkg_resources.DistributionNotFound:
        version = "1.0.0"
    return version
