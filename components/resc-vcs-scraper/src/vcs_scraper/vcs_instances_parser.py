
# Standard Library
import json
import logging
from json import JSONDecodeError
from typing import List

# Third Party
from pydantic import ValidationError

# First Party
from vcs_scraper.model import VCSInstance

logger = logging.getLogger(__name__)


def parse_vcs_instances_file(filepath: str) -> List[VCSInstance]:
    vcs_instances: List[VCSInstance] = []
    errors_found = False
    logger.info(f"Reading VCS instances from file {filepath}")
    try:
        with open(filepath, encoding="utf-8") as vcs_instances_file:
            parsed_vcs_instances = json.loads(vcs_instances_file.read())
            logger.info(f"Parsing VCS instance definitions from file {filepath}")
            for vcs_instance in parsed_vcs_instances:
                try:
                    logger.info(f"Parsing VCS instance '{vcs_instance}'")
                    vcs_instances.append(VCSInstance(**parsed_vcs_instances[vcs_instance]))
                except ValidationError as validation_error:
                    logger.error(f"Failed while parsing VCS instance '{vcs_instance}': {validation_error}")
                    errors_found = True
    except JSONDecodeError as json_error:
        logger.error(f"Failed to parse VCS instances file '{filepath}': {json_error}")
        errors_found = True
    except FileNotFoundError:
        logger.error(f"VCS Instances file not found: '{filepath}'")
        errors_found = True
    if errors_found:
        return []
    return vcs_instances
