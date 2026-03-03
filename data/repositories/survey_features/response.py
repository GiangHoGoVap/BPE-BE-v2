from data.models.survey_feature_models.response_model import (
    Response_model,
    Respondent_model,
)
from database.db import DatabaseConnector


class Response:
    @classmethod
    def create_response(
        cls,
        survey_id,
        respondent_id,
        start_date,
        end_date,
    ):
        session = DatabaseConnector.get_session()
        try:
            response = Response_model(
                survey_id=survey_id,
                respondent_id=respondent_id,
                start_date=start_date,
                end_date=end_date,
                is_deleted=False,
            )
            session.add(response)
            session.commit()
            return response
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_number_of_responses(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            responses = (
                session.query(Response_model)
                .filter(
                    Response_model.survey_id == survey_id,
                    Response_model.is_deleted == False,
                )
                .all()
            )
            session.commit()
            return len(responses)
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_response(cls, response_id):
        session = DatabaseConnector.get_session()
        try:
            response = (
                session.query(Response_model)
                .filter(
                    Response_model.id == response_id,
                    Response_model.is_deleted == False,
                )
                .first()
            )
            session.commit()
            return response
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_responses(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            responses = (
                session.query(Response_model)
                .filter(
                    Response_model.survey_id == survey_id,
                    Response_model.is_deleted == False,
                )
                .all()
            )
            for response in responses:
                response.is_deleted = True
            session.commit()
            return responses
        except Exception as e:
            session.rollback()
            raise Exception(e)
