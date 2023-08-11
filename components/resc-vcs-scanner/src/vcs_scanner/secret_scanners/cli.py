# Standard Library
import getpass
import json
import logging.config
import os
import pathlib
from argparse import ArgumentParser, Namespace
from urllib.parse import urlparse

# Third Party
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

# First Party
from vcs_scanner.common import get_rule_pack_version_from_file, initialise_logs
from vcs_scanner.constants import CLI_VCS_AZURE, CLI_VCS_BITBUCKET, CLI_VCS_LOCAL_SCAN, LOG_FILE_PATH_CLI
from vcs_scanner.helpers.env_default import EnvDefault
from vcs_scanner.model import RepositoryRuntime
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
    """
        Create ArgumentParser for CLI arguments
    :return: ArgumentParser.
        ArgumentParser instance with all arguments as expected for RESC
    """
    parser_common = ArgumentParser(add_help=False)
    parser_common.add_argument("--gitleaks-path", type=pathlib.Path, action=EnvDefault, envvar="RESC_GITLEAKS_PATH",
                               required=True, help="Path to the gitleaks binary. "
                                                   "Can also be set via the RESC_GITLEAKS_PATH environment variable")
    parser_common.add_argument("--gitleaks-rules-path", type=pathlib.Path, action=EnvDefault, required=True,
                               envvar="RESC_GITLEAKS_RULES_PATH", help="Path to the gitleaks rules file. "
                                                                       "Can also be set via the "
                                                                       "RESC_GITLEAKS_RULES_PATH environment variable")
    parser_common.add_argument("-w", "--exit-code-warn", required=False, action=EnvDefault, default=2, type=int,
                               envvar="RESC_EXIT_CODE_WARN",
                               help="Exit code given if CLI encounters findings tagged with Warn, default 2. "
                                    "Can also be set via the RESC_EXIT_CODE_WARN environment variable")
    parser_common.add_argument("-b", "--exit-code-block", required=False, action=EnvDefault, default=1, type=int,
                               envvar="RESC_EXIT_CODE_BLOCK",
                               help="Exit code given if CLI encounters findings tagged with Block, default 1. "
                                    "Can also be set via the RESC_EXIT_CODE_BLOCK environment variable")
    parser_common.add_argument("--filter-tag", required=False, action=EnvDefault, type=str,
                               envvar="RESC_FILTER_TAG",
                               help="Filter for findings based on specified tag. "
                                    "Can also be set via the RESC_FILTER_TAG environment variable")
    parser_common.add_argument("-v", "--verbose", required=False, action="store_true",
                               help="Enable more verbose logging")

    repository_common = ArgumentParser(add_help=False)
    repository_common.add_argument("--repo-name", type=str, required=False, action=EnvDefault, envvar="RESC_REPO_NAME",
                                   help="The name of the repository. "
                                        "Can also be set via the RESC_REPO_NAME environment variable")
    repository_common.add_argument("--force-base-scan", required=False, action="store_true")

    repository_common.add_argument("--rws-url", type=str, required=False, action=EnvDefault, envvar="RESC_RWS_URL",
                                   help="The URL to the secret tracking service to which the scan results should "
                                        "be written. "
                                        "Can also be set via the RESC_RWS_URL environment variable")

    parser: ArgumentParser = ArgumentParser()

    subparser = parser.add_subparsers(title="command", dest="command", required=True, help="Options dir, repo")
    directory = subparser.add_parser("dir", description="Scan a directory", help="Scan a directory",
                                     parents=[parser_common])
    repository = subparser.add_parser("repo", description="Scan a Git repository", help="Scan a Git repository")

    directory.add_argument("--dir", type=pathlib.Path, required=True, action=EnvDefault, envvar="RESC_SCAN_PATH",
                           help="The path to the directory where the scan target. "
                                "Can also be set via the RESC_SCAN_PATH environment variable")

    repository_subparser = repository.add_subparsers(title="repository_location", dest="repository_location",
                                                     required=True, help="Options local, remote")
    repository_local = repository_subparser.add_parser("local", description="Scan a locally already cloned repository",
                                                       help="Scan a locally already cloned repository",
                                                       parents=[parser_common, repository_common])
    repository_remote = repository_subparser.add_parser("remote", description="Scan a remote repository",
                                                        help="Scan a remote repository",
                                                        parents=[parser_common, repository_common])

    repository_local.add_argument("--dir", type=pathlib.Path, required=True, action=EnvDefault, envvar="RESC_SCAN_PATH",
                                  help="The path to the directory where the repo is located. "
                                       "Can also be set via the RESC_SCAN_PATH environment variable")

    repository_remote.add_argument("--repo-url", type=str, required=True, action=EnvDefault, envvar="RESC_REPO_URL",
                                   help="url to repository you want to scan. "
                                        "Can also be set via the RESC_REPO_URL environment variable")
    repository_remote.add_argument("--username", type=str, required=False,
                                   action=EnvDefault, envvar="RESC_REPO_USERNAME",
                                   help="The username used for cloning the repository, "
                                        "you will be prompted for the password. "
                                        "Can also be set via the RESC_REPO_USERNAME & RESC_REPO_PASSWORD environment "
                                        "variable")

    return parser


def get_repository_name_from_url(repo_url: str) -> str:
    """
        Get repository name from given URL, taking the last segment of the url as name
    :param repo_url:
        Full url to the repository
    :return: str.
        The output will the name of the repository based on the url
    """
    url = urlparse(repo_url)
    if url.path.split("/")[-1] == "":
        return url.path.split("/")[-2]
    return url.path.split("/")[-1]


def validate_cli_arguments(args: Namespace):  # pylint: disable=R0912
    """
        Validate the CLI arguments given
    :param args:
        Namespace object containing the arguments parsed from the CLI
    :return: args or False.
        The output will be the args given, unless validation fails then it contains False
    """
    valid_arguments = True
    # Prompt for the password for a remote repo if username is specified
    if args.command == "repo" and args.repository_location == "remote" and args.username:
        if "RESC_REPO_PASSWORD" in os.environ:
            args.password = os.environ["RESC_REPO_PASSWORD"]
        else:
            args.password = getpass.getpass("Password:")

    # Derive the repository name from the directory or url if not provided
    if args.command == "repo" and args.repository_location == "remote" and not args.repo_name:
        args.repo_name = get_repository_name_from_url(args.repo_url)
    elif args.command == "dir" or \
            (args.command == "repo" and args.repository_location == "local" and not args.repo_name):
        if not os.path.isdir(args.dir.absolute()):
            logger.error(f"The directory {args.dir.absolute()} does not exist")
            valid_arguments = False
        args.repo_name = os.path.split(args.dir.absolute())[1]

    if not valid_arguments:
        return False

    return args


def scan_repository_from_cli():
    """
        Startup command for the CLI, parsing arguments and starting the process
    """
    parser: ArgumentParser = create_cli_argparser()
    args: Namespace = parser.parse_args()
    args = validate_cli_arguments(args)

    if args.verbose:
        logger_config.setLevel(logging.DEBUG)
    else:
        logger_config.setLevel(logging.INFO)

    if args.command == "dir":
        logger.info(f"Scanning directory {args.dir.absolute()}")
        scan_directory(args)
    elif args.command == "repo":
        if args.repository_location == "local":
            logger.info(f"Scanning repository local {args.dir.absolute()}")
            args.repo_url = FAKE_URL
            args.username = None
            args.password = None
        elif args.repository_location == "remote":
            logger.info(f"Scanning repository remote {args.repo_url}")
        scan_repository(args)


def scan_directory(args: Namespace):
    """
        Start the process of scanning a non-git directory
    :param args:
        Namespace object containing the CLI arguments
    """
    repository = RepositoryRuntime(
        repository_url=FAKE_URL,
        repository_name="local",
        repository_id="local",
        project_key="local",
        vcs_instance_name="vcs_instance_name",
        latest_commit=FAKE_COMMIT
    )

    output_plugin = STDOUTWriter(toml_rule_file_path=args.gitleaks_rules_path,
                                 exit_code_warn=args.exit_code_warn, exit_code_block=args.exit_code_block,
                                 filter_tag=args.filter_tag)
    with open(args.gitleaks_rules_path, encoding="utf-8") as rule_pack:
        rule_pack_version = get_rule_pack_version_from_file(rule_pack.read())
    if not rule_pack_version:
        rule_pack_version = "0.0.0"

    secret_scanner = SecretScanner(
        gitleaks_binary_path=args.gitleaks_path,
        gitleaks_rules_path=args.gitleaks_rules_path,
        rule_pack_version=rule_pack_version,
        output_plugin=output_plugin,
        repository=repository.convert_to_repository(vcs_instance_id=1),
        username="",
        personal_access_token="",
        local_path=f"{args.dir.absolute()}",
    )

    secret_scanner.run_directory_scan()


def scan_repository(args: Namespace):
    """
        Start the process of scanning a git repository (remote or local)
    :param args:
        Namespace object containing the CLI arguments
    """
    vcs_type = guess_vcs_provider(args.repo_url)
    vcs_name = determine_vcs_name(args.repo_url, vcs_type)

    repository = RepositoryRuntime(
        repository_url=args.repo_url,
        repository_name=args.repo_name,
        repository_id=args.repo_name,
        project_key=args.repo_name,
        vcs_instance_name=vcs_name,
        latest_commit=FAKE_COMMIT
    )

    if args.rws_url:
        output_plugin = RESTAPIWriter(rws_url=args.rws_url)
        rule_pack_version = output_plugin.download_rule_pack()

    else:
        output_plugin = STDOUTWriter(toml_rule_file_path=args.gitleaks_rules_path,
                                     exit_code_warn=args.exit_code_warn, exit_code_block=args.exit_code_block,
                                     filter_tag=args.filter_tag)
        with open(args.gitleaks_rules_path, encoding="utf-8") as rule_pack:
            rule_pack_version = get_rule_pack_version_from_file(rule_pack.read())
    if not rule_pack_version:
        rule_pack_version = "0.0.0"

    secret_scanner = SecretScanner(
        gitleaks_binary_path=args.gitleaks_path,
        gitleaks_rules_path=args.gitleaks_rules_path,
        rule_pack_version=rule_pack_version,
        output_plugin=output_plugin,
        repository=repository.convert_to_repository(vcs_instance_id=1),
        username=args.username,
        personal_access_token=args.password,
        local_path=f"{args.dir.absolute()}",
        force_base_scan=args.force_base_scan,
        latest_commit="unknown"
    )

    secret_scanner.run_repository_scan()


def guess_vcs_provider(repo_url: str) -> VCSProviders:
    """
        Guess the vcs provider based on the url given, defaulted to bitbucket
    :param repo_url:
        Full url of the repository
    :return: VCSProviders.
        The output will contain the guessed VCSProviders enum value
    """
    url = urlparse(repo_url)
    if "bitbucket" in url.netloc:
        return VCSProviders.BITBUCKET
    if "dev.azure" in url.netloc:
        return VCSProviders.AZURE_DEVOPS
    logger.warning("Unable to guess VCS_Provider, assuming it is bitbucket.")
    return VCSProviders.BITBUCKET


def determine_vcs_name(repo_url: str, vcs_type: VCSProviders) -> str:
    """
        Determine the vcs provider name based on the vcs_type given, defaulted to CLI_VCS_LOCAL_SCAN
    :param repo_url:
        Full url of the repository
    :param vcs_type:
        VCSProviders type of the repository
    :return: str.
        The output will contain the name of the vcs provider
    """
    vcs_name = CLI_VCS_LOCAL_SCAN
    if repo_url and repo_url is not FAKE_URL:
        if vcs_type == VCSProviders.AZURE_DEVOPS:
            vcs_name = CLI_VCS_AZURE
        elif vcs_type == VCSProviders.BITBUCKET:
            vcs_name = CLI_VCS_BITBUCKET
    return vcs_name
