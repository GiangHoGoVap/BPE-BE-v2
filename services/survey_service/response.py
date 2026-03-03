from datetime import datetime

from data.repositories.survey_features.response import Response
from data.repositories.survey_features.survey import Survey
from services.survey_service.answer import Answer_service
from services.survey_service.respondent import Respondent_service

# from services.survey_service.survey import Survey_service
from services.survey_service.survey_result import Survey_result_service
from services.utils import Date_time_convert


class Response_service:
    @classmethod
    def submit_survey_form(cls, answers, email, full_name, process_version_version):
        # get survey id from process_version_version
        # add respondent to table Respondent
        # create new response
        # add answers to table Answer. answers is a list of answer objects, each object contains question_id, value
        # calculate scores for the survey
        # return if survey allows respondent to see the result and send another response
        try:
            survey = Survey.check_if_survey_exists(process_version_version)
            if not survey:
                return {"message": "Survey not found"}
            if survey.is_published == "closed":
                return {"message": "Survey is not published"}
            survey_id = survey.id
            new_respondent = Respondent_service.create_respondent(email, full_name)
            respondent_id = new_respondent.id
            end_date = Date_time_convert.get_date_time_now_date()
            new_response = cls.create_response(
                survey_id, respondent_id, end_date, start_date=None
            )
            # add answers
            response_id = new_response.id
            for answer in answers:
                Answer_service.add_answer(
                    response_id, answer["questionInSectionId"], answer["value"]
                )

            # get number of responses
            current_number_of_responses = cls.get_number_of_responses(survey_id)
            # calculate scores
            score = Survey_result_service.calculate_scores(
                survey_id, current_number_of_responses
            )

            # return if survey allows respondent to see the result and send another response
            survey_config = Survey.get_survey_response_config_some(survey_id)
            return {
                "responseId": response_id,
                "incompleteSurveyAction": survey_config.incomplete_survey_action,
                "message": "Survey form submitted successfully",
                "allowDuplicateRespondent": survey_config.allow_duplicate_respondent,
                "sendResultToRespondent": survey_config.send_result_to_respondent,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def create_response(cls, survey_id, respondent_id, end_date, start_date=None):
        return Response.create_response(survey_id, respondent_id, start_date, end_date)

    @classmethod
    def get_number_of_responses(cls, survey_id):
        return Response.get_number_of_responses(survey_id)

    @classmethod
    def get_survey_response(cls, response_id):
        survey_response = Response.get_response(response_id)
        answers_in_response = Answer_service.get_all_answers(survey_response.id)
        return {
            "response": {
                "id": survey_response.id,
                "surveyId": survey_response.survey_id,
                "respondentId": survey_response.respondent_id,
                "startDate": survey_response.start_date,
                "endDate": survey_response.end_date,
            },
            "answers": [
                {
                    "id": answer.id,
                    "responseId": answer.response_id,
                    "questionId": answer.question_id,
                    "value": answer.value,
                }
                for answer in answers_in_response
            ],
        }

    @classmethod
    def delete_responses(cls, survey_id):
        deleted_responses = Response.delete_responses(survey_id)
        return [
            {
                "id": response.id,
            }
            for response in deleted_responses
        ]
