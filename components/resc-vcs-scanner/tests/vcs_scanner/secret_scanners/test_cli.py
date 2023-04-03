# Standard Library
from argparse import ArgumentParser
from pathlib import PosixPath

# Third Party
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders

# First Party
from vcs_scanner.constants import CLI_VCS_AZURE, CLI_VCS_BITBUCKET, CLI_VCS_LOCAL_SCAN
from vcs_scanner.secret_scanners.cli import (
    create_cli_argparser,
    determine_vcs_name,
    get_repository_name_from_url,
    guess_vcs_provider,
    validate_cli_arguments
)


def test_get_repository_name_from_url():
    test_url_1 = "https://fake.repo/project/repository"
    test_url_2 = "https://fake.repo/project/repository/"
    expected_result = "repository"
    result_1 = get_repository_name_from_url(test_url_1)
    result_2 = get_repository_name_from_url(test_url_2)
    assert result_1 == expected_result
    assert result_2 == expected_result


def test_guess_vcs_provider_default():
    test_url = "https://fake.repo/project/repository"
    expected_result = VCSProviders.BITBUCKET
    result = guess_vcs_provider(test_url)
    assert result == expected_result


def test_guess_vcs_provider_ado():
    test_url = "https://dev.azure.com/project/repository"
    expected_result = VCSProviders.AZURE_DEVOPS
    result = guess_vcs_provider(test_url)
    assert result == expected_result


def test_guess_vcs_provider_bitbucket():
    test_url = "https://bitbucket.com/project/repository"
    expected_result = VCSProviders.BITBUCKET
    result = guess_vcs_provider(test_url)
    assert result == expected_result


def test_determine_vcs_name_default():
    result = determine_vcs_name(None, None)
    assert result == CLI_VCS_LOCAL_SCAN


def test_determine_vcs_name_ado():
    test_url = "https://dev.azure.com/project/repository"
    vcs_provider = VCSProviders.AZURE_DEVOPS
    result = determine_vcs_name(test_url, vcs_provider)
    assert result == CLI_VCS_AZURE


def test_determine_vcs_name_bitbucket():
    test_url = "https://bitbucket.com/project/repository"
    vcs_provider = VCSProviders.BITBUCKET
    result = determine_vcs_name(test_url, vcs_provider)
    assert result == CLI_VCS_BITBUCKET


def test_create_cli_argparser_dir():
    parser = create_cli_argparser()
    assert isinstance(parser, ArgumentParser)
    argv = 'dir --gitleaks-path=/tmp --gitleaks-rules-path=/tmp --dir=/tmp'.split()
    args = parser.parse_args(argv)
    args = validate_cli_arguments(args)
    assert args is not False
    assert args.command == "dir"
    assert args.gitleaks_path == PosixPath('/tmp')
    assert args.gitleaks_rules_path == PosixPath('/tmp')
    assert args.dir == PosixPath('/tmp')


def test_create_cli_argparser_repo_local():
    parser = create_cli_argparser()
    assert isinstance(parser, ArgumentParser)
    argv = 'repo local --gitleaks-path=/tmp --gitleaks-rules-path=/tmp --dir=/tmp'.split()
    args = parser.parse_args(argv)
    args = validate_cli_arguments(args)
    assert args is not False
    assert args.command == "repo"
    assert args.repository_location == "local"
    assert args.gitleaks_path == PosixPath('/tmp')
    assert args.gitleaks_rules_path == PosixPath('/tmp')
    assert args.dir == PosixPath('/tmp')


def test_create_cli_argparser_repo_remote():
    parser = create_cli_argparser()
    assert isinstance(parser, ArgumentParser)
    argv = 'repo remote --gitleaks-path=/tmp --gitleaks-rules-path=/tmp --repo-url=https://fake.url/repo'.split()
    args = parser.parse_args(argv)
    args = validate_cli_arguments(args)
    assert args is not False
    assert args.command == "repo"
    assert args.repository_location == "remote"
    assert args.gitleaks_path == PosixPath('/tmp')
    assert args.gitleaks_rules_path == PosixPath('/tmp')
    assert args.repo_url == "https://fake.url/repo"


def test_create_cli_argparser_cli_tag():
    parser = create_cli_argparser()
    assert isinstance(parser, ArgumentParser)
    argv = 'repo remote --gitleaks-path=/f --gitleaks-rules-path=/f --repo-url=https://url/ --filter-tag=Cli'.split()
    args = parser.parse_args(argv)
    args = validate_cli_arguments(args)
    assert args is not False
    assert args.filter_tag == "Cli"
