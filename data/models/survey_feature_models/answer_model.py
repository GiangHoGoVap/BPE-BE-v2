from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from data.models.survey_feature_models.question_model import (
    Question_in_section_model,
)
from data.models.survey_feature_models.response_model import Response_model
from database.db import DatabaseConnector


class Answer_model(Base):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    value: Mapped[str] = mapped_column(nullable=True)

    # foreign key
    response_id: Mapped[int] = mapped_column(ForeignKey("response.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question_in_section.id"), nullable=False
    )

    # relationship
    response = relationship("Response_model", backref="answer")
    question = relationship("Question_in_section_model", backref="answer")


# Base.metadata.create_all(DatabaseConnector.get_engine())
