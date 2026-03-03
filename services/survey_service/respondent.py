from data.repositories.survey_features.respondent import Respondent


class Respondent_service:
    @classmethod
    def create_respondent(cls, email, full_name):
        return Respondent.create_respondent(email, full_name)
