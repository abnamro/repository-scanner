# Third Party
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.branch_info import BranchInfo


class DBbranchInfo(Base):
    __tablename__ = "branch_info"
    id_ = Column("id", Integer, primary_key=True)
    repository_info_id = Column(Integer, ForeignKey("repository_info.id"), nullable=False)
    branch_id = Column(String(200), nullable=False)
    branch_name = Column(String(200), nullable=False)
    last_scanned_commit = Column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint("branch_id", "repository_info_id", name="unique_branch_id_per_repository"),)

    def __init__(self, repository_info_id, branch_id, branch_name, last_scanned_commit):
        self.branch_id = branch_id
        self.repository_info_id = repository_info_id
        self.branch_name = branch_name
        self.last_scanned_commit = last_scanned_commit

    @staticmethod
    def create_from_branch_info(branch_info: BranchInfo, repository_info_id: int):
        db_branch_info = DBbranchInfo(
            repository_info_id=repository_info_id,
            branch_id=branch_info.branch_id,
            branch_name=branch_info.branch_name,
            last_scanned_commit=branch_info.last_scanned_commit
        )
        return db_branch_info
