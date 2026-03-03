import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from data.models.survey_feature_models.survey_model import Process_version_model
from data.models.workspace_model import Workspace_model
from database.db import DatabaseConnector


class Health_model(Base):
    __tablename__ = "health"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    total_score: Mapped[float] = mapped_column(nullable=True)

    current_cycle_time: Mapped[float] = mapped_column(nullable=True)

    current_cost: Mapped[float] = mapped_column(nullable=True)

    current_quality: Mapped[float] = mapped_column(nullable=True)

    current_flexibility: Mapped[float] = mapped_column(nullable=True)

    # foreign key
    # process_portfolio_id: Mapped[int] = mapped_column(
    #     ForeignKey("process_portfolio.id"), nullable=True
    # )
    process_version_version: Mapped[str] = mapped_column(
        ForeignKey("process_version.version"), nullable=True
    )

    # relationship
    process_version = relationship("Process_version_model", backref="health")
    # process_portfolio = relationship("Process_portfolio_model", backref="health")


class Feasibility_model(Base):
    __tablename__ = "feasibility"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    total_score: Mapped[float] = mapped_column(nullable=True)

    # foreign key
    # process_portfolio_id: Mapped[int] = mapped_column(
    #     ForeignKey("process_portfolio.id"), nullable=True
    # )
    process_version_version: Mapped[str] = mapped_column(
        ForeignKey("process_version.version"), nullable=True
    )

    # relationship
    process_version = relationship("Process_version_model", backref="feasibility")
    # process_portfolio = relationship("Process_portfolio_model", backref="feasibility")


class Strategic_importance_model(Base):
    __tablename__ = "strategic_importance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    total_score: Mapped[float] = mapped_column(nullable=True)

    # foreign key
    # process_portfolio_id: Mapped[int] = mapped_column(
    #     ForeignKey("process_portfolio.id"), nullable=True
    # )
    process_version_version: Mapped[str] = mapped_column(
        ForeignKey("process_version.version"), nullable=True
    )

    # relationship
    process_version = relationship(
        "Process_version_model", backref="strategic_importance"
    )
    # process_portfolio = relationship(
    #     "Process_portfolio_model", backref="strategic_importance"
    # )


class Process_portfolio_model(Base):
    __tablename__ = "process_portfolio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    # foreign key
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspace.id"), nullable=True)

    # relationship
    workspace = relationship("Workspace_model", backref="process_portfolio")


# Base.metadata.create_all(DatabaseConnector.get_engine())
