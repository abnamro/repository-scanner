import logging

from argparse import ArgumentParser


from resc_backend.common import initialise_logs
from resc_backend.constants import LOG_FILE_DUMMY_DATA_GENERATOR

logger_config = initialise_logs(LOG_FILE_DUMMY_DATA_GENERATOR)
logger = logging.getLogger(__name__)


class CliParser:

    def __init__(self):
        pass

    @staticmethod
    def create_cli_argparser() -> ArgumentParser:
        """Parses the command line arguments and returns the parser"""
        parser: ArgumentParser = ArgumentParser()
        parser.add_argument("--active-rulepack", type=str, default="2.0.4",
                            required=False,
                            help="Rule pack version to use as active")
        parser.add_argument("--additional-rulepacks", type=str, default="",
                            required=False,
                            help="Specify more rule-packs as comma separated values. Example: 2.0.2,2.0.1....")
        parser.add_argument("--rules-generate-amount", type=int, default=10,
                            required=False,
                            help="Amount of rules to generate")
        parser.add_argument("--vcs-instances-generate-amount", type=int, default=3,
                            required=False,
                            help="Amount of vcs-instances to generate")
        parser.add_argument("--repos-generate-amount", type=int, default=2,
                            required=False,
                            help="Amount of repos to generate")
        parser.add_argument("--max-scans-per-repo-generate-amount", type=int, default=5,
                            required=False,
                            help="Amount of scans to generate")
        parser.add_argument("--findings-generate-amount", type=int, default=100,
                            required=False,
                            help="Amount of findings to generate")
        return parser

