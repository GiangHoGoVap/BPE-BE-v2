from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from data.models.project_model import Project_model
from database.db import DatabaseConnector


class Process_model(Base):
    __tablename__ = "process"

    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    last_saved: Mapped[datetime] = mapped_column(nullable=False)

    # foreign key
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)

    # relationship
    project = relationship("Project_model", backref="process")


class Process_version_model(Base):
    __tablename__ = "process_version"

    id: Mapped[int] = mapped_column(autoincrement=True, unique=True)
    xml_file_link: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    version: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(nullable=True, default=False)
    num: Mapped[int] = mapped_column(nullable=False)
    # foreign key
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id"), nullable=False, primary_key=True
    )
    process_id: Mapped[int] = mapped_column(
        ForeignKey("process.id"), nullable=False, primary_key=True
    )

    # relationship
    project = relationship("Project_model", backref="process_version")
    process = relationship("Process_model", backref="process_version")


# Base.metadata.create_all(DatabaseConnector.get_engine())
