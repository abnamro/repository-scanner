# Third Party
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.repository import Repository


class DBrepository(Base):
    __tablename__ = "repository"
    id_ = Column("id", Integer, primary_key=True)
    vcs_instance = Column(Integer, ForeignKey("vcs_instance.id"), nullable=False)
    project_key = Column(String(100), nullable=False)
    repository_id = Column(String(100), nullable=False)
    repository_name = Column(String(100), nullable=False)
    repository_url = Column(String(200), nullable=False)
    latest_commit = Column(String(100), nullable=True)
    __table_args__ = (UniqueConstraint("project_key", "repository_id", "vcs_instance",
                                       name="unique_repository_id_per_project"),)

    def __init__(self, project_key, repository_id, repository_name, repository_url, vcs_instance):
        self.project_key = project_key
        self.repository_id = repository_id
        self.repository_name = repository_name
        self.repository_url = repository_url
        self.vcs_instance = vcs_instance

    @staticmethod
    def create_from_repository(repository: Repository):
        db_repository = DBrepository(
            project_key=repository.project_key,
            repository_id=repository.repository_id,
            repository_name=repository.repository_name,
            repository_url=repository.repository_url,
            vcs_instance=repository.vcs_instance
        )
        return db_repository
