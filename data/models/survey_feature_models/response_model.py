from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base

from data.models.survey_feature_models.survey_model import Survey_model
from database.db import DatabaseConnector


class Respondent_model(Base):
    __tablename__ = "respondent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    full_name: Mapped[str] = mapped_column(nullable=True)


class Response_model(Base):
    __tablename__ = "response"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True, default=None)

    # foreign key
    survey_id: Mapped[int] = mapped_column(ForeignKey("survey.id"), nullable=False)
    respondent_id: Mapped[int] = mapped_column(
        ForeignKey("respondent.id"), nullable=False
    )

    # relationship
    survey = relationship("Survey_model", backref="response")
    respondent = relationship("Respondent_model", backref="response")


# Base.metadata.create_all(DatabaseConnector.get_engine())
