# Third Party
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

# First Party
from resc_backend.db.model import Base
from resc_backend.resc_web_service.schema.branch import Branch


class DBbranch(Base):
    __tablename__ = "branch"
    id_ = Column("id", Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=False)
    branch_id = Column(String(200), nullable=False)
    branch_name = Column(String(200), nullable=False)
    last_scanned_commit = Column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint("branch_id", "repository_id", name="unique_branch_id_per_repository"),)

    def __init__(self, repository_id, branch_id, branch_name, last_scanned_commit):
        self.branch_id = branch_id
        self.repository_id = repository_id
        self.branch_name = branch_name
        self.last_scanned_commit = last_scanned_commit

    @staticmethod
    def create_from_branch(branch: Branch, repository_id: int):
        db_branch = DBbranch(
            repository_id=repository_id,
            branch_id=branch.branch_id,
            branch_name=branch.branch_name,
            last_scanned_commit=branch.last_scanned_commit
        )
        return db_branch
