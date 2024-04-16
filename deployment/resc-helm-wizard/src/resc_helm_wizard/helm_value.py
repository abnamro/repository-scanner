# Standard Library
from typing import List

# First Party
from resc_helm_wizard.vcs_instance import VcsInstance


class HelmValue:
    """
    A class to represent user provided Helm values.
    Attributes
    ----------
    operating_system : str
        Operating system
    db_password : str
        Database password
    db_storage_path : str
        Database storage path
    rabbitmq_storage_path : str
        Rabbitmq storage path
    vcs_instances : list
        List of VCS instances
    """

    def __init__(
        self,
        operating_system: str,
        db_password: str,
        db_storage_path: str,
        rabbitmq_storage_path: str,
        vcs_instances: List[VcsInstance],
    ):
        self.operating_system: str = operating_system
        self.db_password: str = db_password
        self.db_storage_path: str = db_storage_path
        self.rabbitmq_storage_path: str = rabbitmq_storage_path
        self.vcs_instances: list = vcs_instances
