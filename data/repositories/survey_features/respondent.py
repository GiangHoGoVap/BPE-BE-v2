from data.models.survey_feature_models.response_model import Respondent_model
from database.db import DatabaseConnector


class Respondent:
    @classmethod
    def create_respondent(cls, email, full_name):
        # add respondent to table Respondent
        session = DatabaseConnector.get_session()
        try:
            respondent = Respondent_model(
                email=email,
                full_name=full_name,
                is_deleted=False,
            )
            session.add(respondent)
            session.commit()
            return respondent
        except Exception as e:
            session.rollback()
            raise Exception(e)
