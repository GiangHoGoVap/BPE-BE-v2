from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from database.db import DatabaseConnector


class Project_model(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    create_at: Mapped[datetime] = mapped_column(nullable=False)
    deletedat: Mapped[datetime] = mapped_column(nullable=True, default=None)
    is_delete: Mapped[bool] = mapped_column(nullable=False, default=False)
    ownerid: Mapped[int] = mapped_column(nullable=False)
    workspaceid: Mapped[int] = mapped_column(nullable=False)
    isworkspacedeleted: Mapped[bool] = mapped_column(nullable=False, default=False)


# Base.metadata.create_all(DatabaseConnector.get_engine())
