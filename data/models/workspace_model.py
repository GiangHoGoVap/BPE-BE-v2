from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from data.models.meta_data import Base
from database.db import DatabaseConnector


class Workspace_model(Base):
    __tablename__ = "workspace"

    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    createdat: Mapped[datetime] = mapped_column(nullable=False)
    deletedat: Mapped[datetime] = mapped_column(nullable=True, default=None)
    isdeleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    ownerid: Mapped[int] = mapped_column(nullable=False)
    ispersonal: Mapped[bool] = mapped_column(nullable=False, default=False)
    icon: Mapped[str] = mapped_column(nullable=True, default=None)
    background: Mapped[str] = mapped_column(nullable=True, default=None)
    targeted_cycle_time: Mapped[float] = mapped_column(nullable=True, default=0)
    worst_cycle_time: Mapped[float] = mapped_column(nullable=True, default=None)

    targeted_cost: Mapped[float] = mapped_column(nullable=True, default=0)
    worst_cost: Mapped[float] = mapped_column(nullable=True, default=None)

    targeted_quality: Mapped[float] = mapped_column(nullable=True, default=100)
    worst_quality: Mapped[float] = mapped_column(nullable=True, default=0)

    targeted_flexibility: Mapped[float] = mapped_column(nullable=True, default=100)
    worst_flexibility: Mapped[float] = mapped_column(nullable=True, default=0)
    # relationship


# Base.metadata.create_all(DatabaseConnector.get_engine())
