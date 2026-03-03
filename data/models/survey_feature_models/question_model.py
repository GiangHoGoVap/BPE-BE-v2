from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from database.db import DatabaseConnector

from data.models.survey_feature_models.survey_model import Survey_model
from data.models.user_model import User_model


class Section_model(Base):
    __tablename__ = "section"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    name: Mapped[str] = mapped_column(nullable=False)
    order_in_survey: Mapped[int] = mapped_column(nullable=False)

    # foreign key
    survey_id: Mapped[int] = mapped_column(ForeignKey("survey.id"), nullable=False)

    # relationship
    survey = relationship("Survey_model", backref="section")


class Question_in_section_model(Base):
    __tablename__ = "question_in_section"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    order_in_section: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    is_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    question_type: Mapped[str] = mapped_column(nullable=True)
    # foreign key
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id"), nullable=False)

    # relationship
    question = relationship("Question_model", backref="question_in_section")
    section = relationship("Section_model", backref="question_in_section")


class Question_option_model(Base):
    __tablename__ = "question_option"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    content: Mapped[str] = mapped_column(nullable=False)
    order_in_question: Mapped[int] = mapped_column(nullable=False)

    # foreign key
    question_in_section_id: Mapped[int] = mapped_column(
        ForeignKey("question_in_section.id"), nullable=False
    )

    # relationship
    question_in_section = relationship(
        "Question_in_section_model", backref="question_option"
    )


class Question_option_section_mapping_model(Base):
    __tablename__ = "question_option_section_mapping"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    # foreign key
    question_option_id: Mapped[int] = mapped_column(
        ForeignKey("question_option.id"), nullable=False
    )
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id"), nullable=False)

    # relationship
    question_option = relationship(
        "Question_option_model", backref="question_option_section_mapping"
    )
    section = relationship("Section_model", backref="question_option_section_mapping")


class Question_model(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    content: Mapped[str] = mapped_column(nullable=False)
    question_type: Mapped[str] = mapped_column(nullable=False)
    origin: Mapped[str] = mapped_column(nullable=False)
    domain: Mapped[str] = mapped_column(nullable=False)
    usage_count: Mapped[int] = mapped_column(nullable=False, default=0)
    # foreign key
    contributor_id: Mapped[int] = mapped_column(
        ForeignKey("bpe_user.id"), nullable=True
    )

    # relationship
    contributor = relationship("User_model", backref="question")


# Base.metadata.create_all(DatabaseConnector.get_engine())
