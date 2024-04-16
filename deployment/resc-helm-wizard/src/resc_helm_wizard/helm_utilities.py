# Standard Library
import json
import logging
import subprocess
import sys

# First Party
from resc_helm_wizard import constants

logging.basicConfig(level=logging.INFO)


def install_or_upgrade_helm_release(action: str) -> bool:
    """
        Install or upgrade a helm release
    :param action:
        action to perform like install or upgrade
    :return: bool
        Returns true if install or upgrade succeeded else returns false
    """
    logging.info(f"Running {action}. Please wait for a moment...")
    helm_command = [
        "helm",
        action,
        "--timeout",
        constants.HELM_DEPLOY_TIMEOUT,
        "-n",
        constants.NAMESPACE,
        constants.RELEASE_NAME,
        constants.CHART_NAME,
        "-f",
        constants.VALUES_FILE,
        "--set-file",
        "global.secretScanRulePackConfig=" + constants.RULE_FILE,
    ]
    try:
        output = subprocess.check_output(helm_command)
        logging.info(output.decode("utf-8"))
        return True
    except subprocess.CalledProcessError:
        logging.error(f"An error occurred during {constants.CHART_NAME} deployment")
        return False


def check_helm_release_exists() -> bool:
    """
        Checks if helm release exists or not
    :return: bool
        Returns true if helm release exists else returns false
    """
    output = subprocess.run(
        ["helm", "list", "-f", constants.RELEASE_NAME, "-n", constants.NAMESPACE],
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(constants.RELEASE_NAME in output.stdout.strip())


def get_version_from_downloaded_chart() -> str:
    """
        Get version of the downloaded chart
    :return: str
        Returns version of the downloaded chart
    """
    cmd = (
        f"helm search repo {constants.HELM_REPO_NAME} -n {constants.NAMESPACE} -o json"
    )
    output = subprocess.check_output(cmd, shell=True)
    chart_info = json.loads(output.decode("utf-8"))

    if chart_info:
        return chart_info[0]["version"]
    return None


def add_helm_repository():
    """
    Adds a helm repository
    """
    cmd = [
        "helm",
        "repo",
        "add",
        constants.HELM_REPO_NAME,
        constants.RESC_HELM_REPO_URL,
        "-n",
        constants.NAMESPACE,
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        logging.error("An error occurred while adding the helm repository")
        sys.exit(1)


def update_helm_repository():
    """
    Updates a helm repository
    """
    cmd = ["helm", "repo", "update", "-n", constants.NAMESPACE]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        logging.error("An error occurred while updating the helm repository")
        sys.exit(1)


def validate_helm_deployment_status():
    """
    Validate the status of the helm deployment
    """
    try:
        result = subprocess.run(
            ["helm", "status", constants.RELEASE_NAME, "-n", constants.NAMESPACE],
            capture_output=True,
            check=True,
            text=True,
        )
        output = result.stdout.strip()
        if "STATUS: deployed" in output:
            logging.info(
                "The deployment was successful. Visit http://127.0.0.1:30000 to get started with RESC!"
            )
            logging.info(
                "Refer this link for more information on how to trigger the scan: "
                "https://github.com/abnamro/repository-scanner/tree/main/"
                "deployment/kubernetes#trigger-scanning"
            )
    except subprocess.CalledProcessError:
        logging.error(
            "An error occurred during deployment. Please run this command to debug any issue: "
            "kubectl get pods -n resc"
        )
        sys.exit(1)
