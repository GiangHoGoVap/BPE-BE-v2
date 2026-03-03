from data.models.survey_feature_models.answer_model import Answer_model
from data.models.survey_feature_models.question_model import (
    Section_model,
    Question_in_section_model,
)
from data.models.survey_feature_models.survey_model import (
    Survey_model,
    Survey_result_model,
)
from database.db import DatabaseConnector


class Survey_result:
    @classmethod
    def calculate_scores(cls, response_id):
        pass

    @classmethod
    def get_list_of_weight_and_answers_of_questions_in_survey(
        cls, survey_id, question_type
    ):
        session = DatabaseConnector.get_session()
        try:
            # get all questions in all sections belong to survey_id
            # join question and section
            list_of_weight_and_answers_of_questions_in_survey = (
                session.query(
                    Question_in_section_model.id,
                    Answer_model.value,
                    Question_in_section_model.weight,
                )
                .join(
                    Question_in_section_model,
                    Question_in_section_model.id == Answer_model.question_id,
                )
                .join(
                    Section_model,
                    Question_in_section_model.section_id == Section_model.id,
                )
                .filter(
                    Section_model.survey_id == survey_id,
                    Question_in_section_model.question_type == question_type,
                    Question_in_section_model.is_deleted == False,
                    Section_model.is_deleted == False,
                )
                .all()
            )
            session.commit()
            return list_of_weight_and_answers_of_questions_in_survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_weights_of_scores(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            weights_of_scores = (
                session.query(
                    Survey_model.ces_weight,
                    Survey_model.csat_weight,
                    Survey_model.nps_weight,
                )
                .filter(
                    Survey_model.id == survey_id,
                    Survey_model.is_deleted == False,
                )
                .first()
            )
            session.commit()
            return weights_of_scores
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_survey_result(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey_result = (
                session.query(
                    Survey_result_model.ces_score,
                    Survey_result_model.csat_score,
                    Survey_result_model.nps_score,
                    Survey_result_model.total_score,
                )
                .filter(
                    Survey_result_model.survey_id == survey_id,
                )
                .first()
            )
            session.commit()
            return survey_result
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_scores(cls, survey_id, ces_score, nps_score, csat_score, total_score):
        session = DatabaseConnector.get_session()
        try:
            survey_result = (
                session.query(Survey_result_model)
                .filter(Survey_result_model.survey_id == survey_id)
                .first()
            )
            survey_result.ces_score = ces_score
            survey_result.nps_score = nps_score
            survey_result.csat_score = csat_score
            survey_result.total_score = total_score
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def create_survey_result(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey_result = Survey_result_model(
                survey_id=survey_id,
                ces_score=0,
                csat_score=0,
                nps_score=0,
                total_score=0,
                is_visible=False,
            )
            session.add(survey_result)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def check_if_survey_result_exists(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey_result = (
                session.query(Survey_result_model)
                .filter(Survey_result_model.survey_id == survey_id)
                .first()
            )
            session.commit()
            return survey_result
        except Exception as e:
            session.rollback()
            raise Exception(e)
