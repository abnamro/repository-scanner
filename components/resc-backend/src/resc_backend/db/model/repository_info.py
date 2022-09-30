# Third Party
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.repository_info import RepositoryInfo


class DBrepositoryInfo(Base):
    __tablename__ = "repository_info"
    id_ = Column("id", Integer, primary_key=True)
    vcs_instance = Column(Integer, ForeignKey("vcs_instance.id"), nullable=False)
    project_key = Column(String(100), nullable=False)
    repository_id = Column(String(100), nullable=False)
    repository_name = Column(String(100), nullable=False)
    repository_url = Column(String(200), nullable=False)
    __table_args__ = (UniqueConstraint("project_key", "repository_id", "vcs_instance",
                                       name="unique_repository_id_per_project"),)

    def __init__(self, project_key, repository_id, repository_name, repository_url, vcs_instance):
        self.project_key = project_key
        self.repository_id = repository_id
        self.repository_name = repository_name
        self.repository_url = repository_url
        self.vcs_instance = vcs_instance

    @staticmethod
    def create_from_repository_info(repository_info: RepositoryInfo):
        db_repository_info = DBrepositoryInfo(
            project_key=repository_info.project_key,
            repository_id=repository_info.repository_id,
            repository_name=repository_info.repository_name,
            repository_url=repository_info.repository_url,
            vcs_instance=repository_info.vcs_instance
        )
        return db_repository_info
