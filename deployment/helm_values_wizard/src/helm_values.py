class HelmValues():
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
    github_username : str
        GitHub username
    github_token : str
        GitHub token
    """

    def __init__(self,
                 operating_system: str,
                 db_password: str,
                 db_storage_path: str,
                 rabbitmq_storage_path: str,
                 github_username: str,
                 github_token: str):
        self.operating_system: str = operating_system
        self.db_password: str = db_password
        self.db_storage_path: str = db_storage_path
        self.rabbitmq_storage_path: str = rabbitmq_storage_path
        self.github_username: str = github_username
        self.github_token: str = github_token
