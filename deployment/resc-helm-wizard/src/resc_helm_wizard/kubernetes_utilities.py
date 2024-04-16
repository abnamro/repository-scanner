# Standard Library
import logging
import subprocess

logging.basicConfig(level=logging.INFO)


def create_namespace_if_not_exists(namespace_name: str) -> bool:
    """
        Create a namespace if not exists
    :param namespace_name:
        name of the namespace you want to create
    :return: bool
        Returns true if namespace created else returns false
    """
    created = False
    # Check if the namespace already exists
    check_namespace = subprocess.run(
        ["kubectl", "get", "namespace", namespace_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if "NotFound" in check_namespace.stderr:
        # Namespace doesn't exist, create it
        create_namespace = subprocess.run(
            ["kubectl", "create", "namespace", namespace_name], check=True
        )
        if create_namespace.returncode == 0:
            created = True
            logging.info(
                f"Namespace {namespace_name} created. Preparing for deployment..."
            )
        else:
            logging.error(
                f"Error reading namespace: {namespace_name}. Aborting deployment..."
            )
    else:
        created = True
        logging.info(
            f"Namespace {namespace_name} already exists. Preparing for deployment..."
        )
    return created
