from data.models.survey_feature_models.question_model import (
    Question_option_section_mapping_model,
)
from database.db import DatabaseConnector


class Question_option_section_mapping:
    @classmethod
    def create_sample_question_option_section_mapping(cls, question_option, section_id):
        session = DatabaseConnector.get_session()
        try:
            question_option_section_mapping = Question_option_section_mapping_model(
                question_option_id=question_option.id,
                section_id=section_id,
                is_deleted=question_option.is_deleted,
            )
            session.add(question_option_section_mapping)
            session.commit()
            return question_option_section_mapping
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_question_option_section_mapping(cls, question_in_section_id):
        session = DatabaseConnector.get_session()
        try:
            question_option_section_mapping = (
                session.query(Question_option_section_mapping_model)
                .filter(
                    Question_option_section_mapping_model.question_option_id
                    == question_in_section_id
                )
                .first()
            )
            if question_option_section_mapping:
                question_option_section_mapping.is_deleted = True
            session.commit()
            return question_option_section_mapping
        except Exception as e:
            session.rollback()
            raise Exception(e)
