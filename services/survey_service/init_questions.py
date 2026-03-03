from data.models.survey_feature_models.question_model import (
    Question_model,
    Question_option_model,
)
from database.db import DatabaseConnector
from services.survey_service.init_question_data import (
    init_questions,
    init_questions_options,
)


class Initialize:
    @classmethod
    def initialize_questions(cls):
        session = DatabaseConnector.get_session()
        try:
            for sample_question in init_questions:
                question = Question_model(
                    content=sample_question["content"],
                    question_type=sample_question["question_type"],
                    is_deleted=sample_question["is_deleted"],
                    origin=sample_question["origin"],
                    domain=sample_question["domain"],
                    contributor_id=sample_question["contributor_id"],
                    usage_count=sample_question["usage_count"],
                )
                session.add(question)
            session.commit()
            session.close()
            return "Questions have been initialized"
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def initialize_question_options(cls):
        session = DatabaseConnector.get_session()
        try:
            for sample_question_option in init_questions_options:
                question_option = Question_option_model(
                    content=sample_question_option["content"],
                    is_deleted=sample_question_option["is_deleted"],
                    order_in_question=sample_question_option["order_in_question"],
                    question_in_section_id=sample_question_option["question_id"],
                )
                session.add(question_option)
            session.commit()
            session.close()
            return "Question options have been initialized"
        except Exception as e:
            session.rollback()
            raise Exception(e)
