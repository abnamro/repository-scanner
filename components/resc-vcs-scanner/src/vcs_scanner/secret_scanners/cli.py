
# Standard Library
import getpass
import json
import logging.config
import os
import sys
from argparse import ArgumentParser, Namespace
from urllib.parse import urlparse

# Third Party
from resc_backend.resc_web_service.schema.branch import Branch
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

# First Party
from vcs_scanner.common import get_rule_pack_version_from_file, initialise_logs
from vcs_scanner.constants import CLI_VCS_AZURE, CLI_VCS_BITBUCKET, CLI_VCS_LOCAL_SCAN, LOG_FILE_PATH_CLI
from vcs_scanner.model import RepositoryRuntime
from vcs_scanner.secret_scanners.configuration import GITLEAKS_PATH
from vcs_scanner.secret_scanners.rws_api_writer import RESTAPIWriter
from vcs_scanner.secret_scanners.secret_scanner import SecretScanner
from vcs_scanner.secret_scanners.stdout_writer import STDOUTWriter

logger_config = initialise_logs(LOG_FILE_PATH_CLI)
logger = logging.getLogger(__name__)

FAKE_COMMIT = "hash"
FAKE_URL = "http://fake-host.none"


def deserialize_repository_from_file(filepath: str) -> RepositoryRuntime:
    with open(filepath, encoding="utf-8") as repo_file:
        repository_str: str = repo_file.read()
    repository: RepositoryRuntime = RepositoryRuntime(**json.loads(repository_str))
    return repository


def create_cli_argparser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--repo-info", type=str,
                        help="Path to the JSON file containing the repository info")
    parser.add_argument("--repo-url", type=str,
                        help="url to repository you want to scan", default=FAKE_URL)
    parser.add_argument("--repo-dir", type=str,
                        help="The path to the directory where the repo is located")
    parser.add_argument("--repo-name", type=str,
                        help="The name of the repository")
    parser.add_argument("--rws-url", type=str,
                        help="The URL to the secret tracking service to which the scan results should be written")
    parser.add_argument("--vcs-instances", type=str,
                        help="Path to the json file containing the vcs instances definitions")
    parser.add_argument("--temporary-path", type=str, default="/tmp")
    parser.add_argument("--username", type=str, required=False)
    parser.add_argument("--password", action='store_true', required=False)
    parser.add_argument("--branches", default=["master"], nargs="+")
    parser.add_argument("--gitleaks-path", default="./gitleaks",
                        help=f"Path to the gitleaks binary. Can also be provided via the {GITLEAKS_PATH} "
                             f"environment variable")
    parser.add_argument("--gitleaks-rules-path", required=True,
                        help="Path to the gitleaks rules file.")
    parser.add_argument("--force-base-scan", action="store_true")

    return parser


def get_repository_name_from_url(repo_url: str) -> str:
    url = urlparse(repo_url)
    if url.path.split("/")[-1] == "":
        return url.path.split("/")[-2]
    return url.path.split("/")[-1]


def validate_cli_arguments(args: Namespace):  # pylint: disable=R0912
    valid_arguments = True
    if not (args.repo_dir or args.repo_url is not FAKE_URL):
        logger.error("A repository url or a repository directory need to be specified")
        valid_arguments = False
    if args.repo_dir and (args.password or args.username):
        logger.error("Credentials should not be provided for scanning locally cloned repository")
        valid_arguments = False
    if args.username and not args.password or args.password and not args.username:
        logger.error("Both a username and a password need to be provided")
        valid_arguments = False
    if args.username and args.password:
        args.password = getpass.getpass("Password:")
    if args.repo_url is not FAKE_URL and not (args.username and args.password):
        logger.info("A repo url is provided without credentials, assuming the repository is public")

    if args.gitleaks_path and not os.path.isfile(args.gitleaks_path):
        logger.error(f"Could not locate Gitleaks binary path: {args.gitleaks_path}")
        valid_arguments = False
    if args.gitleaks_rules_path and not os.path.isfile(args.gitleaks_rules_path):
        logger.error(f"Could not locate Gitleaks rules path: {args.gitleaks_rules_path}")
        valid_arguments = False
    if not args.repo_name:
        if args.repo_dir:
            if not os.path.isdir(args.repo_dir):
                logger.error(f"The directory {args.repo_dir} does not exist")
                valid_arguments = False
            args.repo_name = os.path.split(args.repo_dir)[1]
        elif args.repo_url is not FAKE_URL:
            args.repo_name = get_repository_name_from_url(args.repo_url)

    if args.repo_info:
        logger.error("The --repo-info flag is not supported yet")
        valid_arguments = False
    if not valid_arguments:
        return False

    return args


def scan_repository_from_cli():
    parser: ArgumentParser = create_cli_argparser()
    args: Namespace = parser.parse_args()
    args = validate_cli_arguments(args)
    if not args:
        logger.error("CLI arguments validation failed")
        sys.exit(-1)
    logger.debug("CLI arguments validation succeeded")
    branches = []
    for i, branch in enumerate(args.branches):
        logger.info(f"Adding branch {branch} to the list of branches to be scanned")
        branches.append(
            Branch(**{"branch_name": branch, "branch_id": i, "latest_commit": FAKE_COMMIT})
        )

    vcs_type = guess_vcs_provider(args.repo_url)
    vcs_name = determine_vcs_name(args.repo_url, vcs_type)

    repository = RepositoryRuntime(
        repository_url=args.repo_url,
        repository_name=args.repo_name,
        repository_id=args.repo_name,
        project_key=args.repo_name,
        vcs_instance_name=vcs_name,
        branches=branches

    )

    if args.rws_url:
        output_plugin = RESTAPIWriter(rws_url=args.rws_url)
        rule_pack_version = output_plugin.download_rule_pack()

    else:
        output_plugin = STDOUTWriter()
        with open(args.gitleaks_rules_path, encoding="utf-8") as rule_pack:
            rule_pack_version = get_rule_pack_version_from_file(rule_pack.read())

    secret_scanner = SecretScanner(
        gitleaks_binary_path=args.gitleaks_path,
        gitleaks_rules_path=args.gitleaks_rules_path,
        rule_pack_version=rule_pack_version,
        output_plugin=output_plugin,
        repository=repository.convert_to_repository(vcs_instance_id=1),
        username=args.username,
        personal_access_token=args.password,
        local_path=args.repo_dir,
        force_base_scan=args.force_base_scan
    )

    secret_scanner.run_repository_scan()


def guess_vcs_provider(repo_url: str) -> VCSProviders:

    url = urlparse(repo_url)
    if "bitbucket" in url.netloc:
        return VCSProviders.BITBUCKET
    if "dev.azure" in url.netloc:
        return VCSProviders.AZURE_DEVOPS
    logger.warning("Unable to guess VCS_Provider, assuming it is bitbucket.")
    return VCSProviders.BITBUCKET


def determine_vcs_name(repo_url: str, vcs_type: VCSProviders) -> str:
    vcs_name = CLI_VCS_LOCAL_SCAN
    if repo_url is not FAKE_URL:
        if vcs_type == VCSProviders.AZURE_DEVOPS:
            vcs_name = CLI_VCS_AZURE
        elif vcs_type == VCSProviders.BITBUCKET:
            vcs_name = CLI_VCS_BITBUCKET
    return vcs_name
