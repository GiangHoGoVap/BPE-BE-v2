from datetime import datetime
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from data.models.meta_data import Base
from database.db import DatabaseConnector
from data.models.project_model import Project_model
from data.models.process_model import Process_version_model


class Survey_model(Base):
    __tablename__ = "survey"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    end_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    is_published: Mapped[str] = mapped_column(nullable=False, default="closed")
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    allow_duplicate_respondent: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    send_result_to_respondent: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    survey_url: Mapped[str] = mapped_column(nullable=True, default="")
    ces_weight: Mapped[float] = mapped_column(nullable=True, default=round(1 / 3, 3))
    nps_weight: Mapped[float] = mapped_column(nullable=True, default=round(1 / 3, 3))
    csat_weight: Mapped[float] = mapped_column(nullable=True, default=round(1 / 3, 3))
    domain: Mapped[str] = mapped_column(nullable=False, default="general")
    incomplete_survey_action: Mapped[str] = mapped_column(nullable=True, default=None)
    last_saved: Mapped[datetime] = mapped_column(nullable=True, default=None)
    # foreign key
    process_version_version: Mapped[str] = mapped_column(
        ForeignKey("process_version.version")
    )

    # relationship
    process_version = relationship("Process_version_model", backref="survey")


class Survey_result_model(Base):
    __tablename__ = "survey_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ces_score: Mapped[float] = mapped_column(nullable=True, default=None)
    nps_score: Mapped[float] = mapped_column(nullable=True, default=None)
    csat_score: Mapped[float] = mapped_column(nullable=True, default=None)
    total_score: Mapped[float] = mapped_column(nullable=True, default=None)
    is_visible: Mapped[bool] = mapped_column(nullable=False, default=False)
    # foreign key
    survey_id: Mapped[int] = mapped_column(ForeignKey("survey.id"), nullable=False)
    # relationship
    survey = relationship("Survey_model", backref="survey_result")


class Survey_recipient_model(Base):
    __tablename__ = "survey_recipient"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    # relationship


class Survey_recipient_association_model(Base):
    __tablename__ = "survey_recipient_association"

    survey_recipient_id: Mapped[int] = mapped_column(
        ForeignKey("survey_recipient.id"), nullable=False
    )
    survey_id: Mapped[int] = mapped_column(ForeignKey("survey.id"), nullable=False)

    # primary key
    __table_args__ = (PrimaryKeyConstraint("survey_recipient_id", "survey_id"),)

    # relationship
    survey_recipient = relationship(
        "Survey_recipient_model", backref="survey_recipient_association"
    )
    survey = relationship("Survey_model", backref="survey_recipient_association")


# Base.metadata.create_all(DatabaseConnector.get_engine())
