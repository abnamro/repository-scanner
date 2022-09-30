# pylint: disable=R0902
# Third Party
from sqlalchemy import Column, Enum, Integer, String, Text, UniqueConstraint

# First Party
from resc_backend.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC
from resc_backend.db.model import Base


class DBVcsInstance(Base):
    __tablename__ = "vcs_instance"
    id_ = Column("id", Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    provider_type = Column(Enum(BITBUCKET, AZURE_DEVOPS, GITHUB_PUBLIC, name="provider_type"))
    scheme = Column(String(50), nullable=False)
    hostname = Column(String(200), nullable=False)
    port = Column(Integer, nullable=False)
    organization = Column(String(200), nullable=True)
    scope = Column("vcs_scope", Text, nullable=True)
    exceptions = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("provider_type", "scheme", "hostname", "port", "organization",
                                       name="unique_vcs_instance"),)

    def __init__(self, name: str, provider_type: str, scheme: str, hostname: str, port: int, organization: str,
                 scope: str, exceptions: str):
        self.name = name
        self.provider_type = provider_type
        self.scheme = scheme
        self.hostname = hostname
        self.port = port
        self.organization = organization
        self.scope = scope
        self.exceptions = exceptions
