from datetime import datetime

from data.models.survey_feature_models.survey_model import Survey_model
from sqlalchemy import and_
from database.db import DatabaseConnector


class Survey:
    @classmethod
    def get_survey_detail(cls, process_version_version):
        # get survey detail
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(
                    Survey_model.process_version_version == process_version_version,
                    Survey_model.is_deleted == False,
                )
                .first()
            )
            session.commit()
            if survey is None:
                return None
            return {
                "id": survey.id,
                "name": survey.name,
                "description": survey.description,
                "createdAt": survey.created_at,
                "isDeleted": survey.is_deleted,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
                "isPublished": survey.is_published,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def create_new_survey(cls, process_version_version):
        # create new survey
        session = DatabaseConnector.get_session()
        try:
            survey = Survey_model(
                name="Survey for Process Version: " + process_version_version,
                description="This is the default description for the survey.",
                process_version_version=process_version_version,
                created_at=datetime.now(),
                is_deleted=False,
                is_published="closed",
                survey_url="",
                start_date=None,
                end_date=None,
                allow_duplicate_respondent=False,
                send_result_to_respondent=False,
                ces_weight=1,
                nps_weight=1,
                csat_weight=1,
                domain="general",
                incomplete_survey_action="delete",
                last_saved=None,
            )
            session.add(survey)
            session.commit()
            session.close()
            return {
                "id": survey.id,
                "name": survey.name,
                "description": survey.description,
                # "createdAt": survey.created_at,
                # "isDeleted": survey.is_deleted,
                # "startDate": survey.start_date,
                # "endDate": survey.end_date,
                "isPublished": survey.is_published,
                "processVersionVersion": survey.process_version_version,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_survey(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.is_deleted = True
            session.commit()
            return {"message": "Survey is deleted"}
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def config_survey_general(
        cls,
        survey_id,
        survey_name,
        survey_description,
        nps_weight,
        ces_weight,
        csat_weight,
    ):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            if survey is None:
                return None
            if survey_name is not None:
                survey.name = survey_name
            if survey_description is not None:
                survey.description = survey_description
            if nps_weight is not None:
                survey.nps_weight = nps_weight
            if ces_weight is not None:
                survey.ces_weight = ces_weight
            if csat_weight is not None:
                survey.csat_weight = csat_weight
            session.commit()
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def config_survey_response(
        cls,
        survey_id,
        incomplete_survey_action,
        allow_duplicate_respondent,
        send_result_to_respondent,
        start_date,
        end_date,
    ):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            if survey is None:
                return None
            if incomplete_survey_action is not None:
                survey.incomplete_survey_action = incomplete_survey_action
            if allow_duplicate_respondent is not None:
                survey.allow_duplicate_respondent = allow_duplicate_respondent
            if send_result_to_respondent is not None:
                survey.send_result_to_respondent = send_result_to_respondent
            if start_date is not None:
                survey.start_date = start_date
            if end_date is not None:
                survey.end_date = end_date
            session.commit()
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def check_if_survey_exists(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(
                    Survey_model.process_version_version == process_version_version,
                    Survey_model.is_deleted == False,
                )
                .first()
            )
            session.commit()
            if survey is None:
                return None
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_survey_general_config(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            session.commit()
            if survey is None:
                return None
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_survey_response_config(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            session.commit()
            if survey is None:
                return None
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_survey_response_config_some(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(
                    Survey_model.incomplete_survey_action,
                    Survey_model.allow_duplicate_respondent,
                    Survey_model.send_result_to_respondent,
                )
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            session.commit()
            if survey is None:
                return None
            return survey
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def publish_survey(cls, survey_id, start_date, end_date, survey_url, is_published):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.is_published = is_published
            survey.start_date = start_date
            survey.end_date = end_date
            survey.survey_url = survey_url
            session.commit()
            return {
                "id": survey.id,
                "isPublished": survey.is_published,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
                "surveyUrl": survey.survey_url,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def close_publish_survey(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.is_published = "closed"
            session.commit()
            return {
                "id": survey.id,
                "isPublished": survey.is_published,
                "endDate": survey.end_date,
                "startDate": survey.start_date,
                "allowDuplicateRespondent": survey.allow_duplicate_respondent,
                "sendResultToRespondent": survey.send_result_to_respondent,
                "incompleteSurveyAction": survey.incomplete_survey_action,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def set_survey_published(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.is_published = "published"
            session.commit()
            return {
                "id": survey.id,
                "isPublished": survey.is_published,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
                "surveyUrl": survey.survey_url,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_unpublished_surveys(cls):
        session = DatabaseConnector.get_session()
        try:
            surveys = (
                session.query(Survey_model)
                .filter(
                    Survey_model.is_published == "pending",
                    Survey_model.is_deleted == False,
                )
                .all()
            )
            session.commit()
            return surveys
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def set_survey_closed(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.is_published = "closed"
            session.commit()
            return {
                "id": survey.id,
                "isPublished": survey.is_published,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_published_surveys(cls):
        session = DatabaseConnector.get_session()
        try:
            surveys = (
                session.query(Survey_model)
                .filter(
                    Survey_model.is_published == "published",
                    Survey_model.is_deleted == False,
                )
                .all()
            )
            session.commit()
            return surveys
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def reset_dates(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            survey = (
                session.query(Survey_model)
                .filter(Survey_model.id == survey_id, Survey_model.is_deleted == False)
                .first()
            )
            survey.start_date = None
            survey.end_date = None
            session.commit()
            return {
                "id": survey.id,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)
