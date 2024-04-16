# Standard Library
from typing import List


class VcsInstance:
    """
    A class to represent VCS instance.
    Attributes
    ----------
    provider_type : str
        vcs provider type
    scheme : str
        scheme of vcs instance
    host : str
        host of vcs instance
    port : str
        port of vcs instance
    username : str
        username of vcs instance
    password : str
        password of vcs instance
    organization : str
        organization of vcs instance
    scope : list
        List of scope
    """

    def __init__(
        self,
        provider_type: str,
        scheme: str,
        host: str,
        port: str,
        username: str,
        password: str,
        organization: str,
        scope: List[str],
    ):
        self.provider_type: str = provider_type
        self.scheme: str = scheme
        self.host: str = host
        self.port: str = port
        self.username: str = username
        self.password: str = password
        self.organization: str = organization
        self.scope: list = scope
