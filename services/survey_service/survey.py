from datetime import datetime

from data.repositories.survey_features.question_option import Question_option
from data.repositories.survey_features.survey import Survey
from services.survey_service.answer import Answer_service
from services.survey_service.question_in_section import (
    Question_in_section_service,
)
from services.survey_service.question_option import Question_option_service
from services.survey_service.response import Response_service
from services.survey_service.section import Section_service
from services.survey_service.survey_recipient import (
    Survey_recipient_service,
    Survey_send_service,
)
from services.utils import Permission_check, Date_time_convert
from smtp.email import Email


class Survey_service:
    @classmethod
    def validate_start_date_end_date(cls, start_date, end_date):
        try:
            current = Date_time_convert.get_date_time_now_date()
            if start_date is not None and (
                start_date < current
                or (start_date == current and start_date.time() < current.time())
            ):
                return {
                    "message": "Start date must be in the future",
                }
            if (
                end_date is not None
                and end_date < current
                or (end_date == current and end_date.time() < current.time())
            ):
                return {
                    "message": "End date must be in the future",
                }
            if (
                start_date is not None
                and end_date is not None
                and (
                    start_date > end_date
                    or (start_date == end_date and start_date.time() > end_date.time())
                )
            ):
                return {
                    "message": "Start date must be before end date",
                }
            return None
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_survey_detail(cls, process_version_version, project_id, user_id):
        # check if user has access to the survey
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")
        # get survey detail
        return Survey.get_survey_detail(process_version_version)

    @classmethod
    def create_new_survey(
        cls,
        project_id,
        user_id,
        process_version_version,
    ):
        # check if user has access to the survey
        is_user_has_access = Permission_check.check_user_has_access_survey(
            project_id, user_id
        )
        if not is_user_has_access:
            raise Exception("User has no access to the survey")
        # create new survey with default name and description
        # default name is: "Survey for process version: {process_version_version}"

        new_survey = Survey.create_new_survey(process_version_version)
        # create sections for the survey
        sections_list_in_survey = Section_service.create_sample_sections(
            new_survey["id"]
        )
        # create questions and question options in each section for the survey
        questions_list_in_survey = Question_in_section_service.create_sample_questions(
            sections_list_in_survey
        )
        # return list of sections, questions and question options in the survey
        return {
            "survey": new_survey,
            "sections": sections_list_in_survey,
            "questions": questions_list_in_survey,
        }

    @classmethod
    def get_survey_content(cls, user_id, project_id, process_version_version):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")
        survey_info = cls.get_survey_detail(
            process_version_version, project_id, user_id
        )
        if survey_info is None:
            return {"message": "Survey does not exist."}
        survey_id = survey_info["id"]
        sections_list_in_survey = Section_service.get_sections_in_survey(survey_id)
        questions_list_in_survey = Question_in_section_service.get_questions_in_survey(
            sections_list_in_survey
        )
        return {
            # "sections": sections_list_in_survey,
            "survey": survey_info,
            "questions": questions_list_in_survey,
        }

    @classmethod
    def delete_survey(cls, user_id, project_id, survey_id):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        # delete all responses
        deleted_responses = Response_service.delete_responses(survey_id)
        # delete all sections
        deleted_sections = Section_service.delete_sections(survey_id)
        # delete all questions
        for section in deleted_sections:
            deleted_questions = Question_in_section_service.delete_questions_in_section(
                section["id"]
            )
            for question in deleted_questions:
                if question["question_type"] in ["multiple_choice", "branching"]:
                    # delete all question options
                    Question_option_service.delete_question_options(question["id"])
        # delete all answers
        for response in deleted_responses:
            Answer_service.delete_answers(response["id"])

        return Survey.delete_survey(survey_id)

    @classmethod
    def config_survey_general(
        cls,
        survey_id,
        user_id,
        project_id,
        survey_name=None,
        survey_description=None,
        nps_weight=None,
        ces_weight=None,
        csat_weight=None,
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        try:
            survey = Survey.config_survey_general(
                survey_id,
                survey_name,
                survey_description,
                nps_weight,
                ces_weight,
                csat_weight,
            )
            if survey is None:
                return None
            return {
                "id": survey.id,
                "name": survey.name,
                "description": survey.description,
                "createdAt": survey.created_at,
                "isDeleted": survey.is_deleted,
                "npsWeight": survey.nps_weight,
                "cesWeight": survey.ces_weight,
                "csatWeight": survey.csat_weight,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def config_survey_response(
        cls,
        survey_id,
        user_id,
        project_id,
        incomplete_survey_action=None,
        allow_duplicate_respondent=None,
        send_result_to_respondent=None,
        start_date=None,
        end_date=None,
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        try:
            validation_result = cls.validate_start_date_end_date(start_date, end_date)
            if validation_result is not None:
                return validation_result

            survey = Survey.config_survey_response(
                survey_id,
                incomplete_survey_action,
                allow_duplicate_respondent,
                send_result_to_respondent,
                start_date,
                end_date,
            )
            if survey is None:
                return None
            return {
                "id": survey.id,
                "incompleteSurveyAction": survey.incomplete_survey_action,
                "allowDuplicateRespondent": survey.allow_duplicate_respondent,
                "sendResultToRespondent": survey.send_result_to_respondent,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def check_if_survey_exists(cls, process_version_version):
        return Survey.check_if_survey_exists(process_version_version)

    @classmethod
    def get_survey_general_config(cls, survey_id, user_id, project_id):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")
        try:
            survey = Survey.get_survey_general_config(survey_id)
            if survey is None:
                return None
            return {
                "id": survey.id,
                "name": survey.name,
                "description": survey.description,
                "createdAt": survey.created_at,
                "isDeleted": survey.is_deleted,
                "npsWeight": survey.nps_weight,
                "cesWeight": survey.ces_weight,
                "csatWeight": survey.csat_weight,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_survey_response_config(cls, survey_id, user_id, project_id):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        try:
            survey = Survey.get_survey_response_config(survey_id)
            if survey is None:
                return None
            return {
                "id": survey.id,
                "incompleteSurveyAction": survey.incomplete_survey_action,
                "allowDuplicateRespondent": survey.allow_duplicate_respondent,
                "sendResultToRespondent": survey.send_result_to_respondent,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
                "isPublished": survey.is_published,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_survey_questions_by_section_id(cls, section_id):
        questions_in_section = Question_in_section_service.get_questions_in_section(
            section_id
        )
        question_options_list = []
        for question in questions_in_section:
            if question.question_type in ["multiple_choice", "branching"]:
                question_options = (
                    Question_option.get_question_options_in_question_in_section(
                        question.id
                    )
                )
                question_options_list.append(question_options)
        return {
            "sectionId": int(section_id),
            "questions": [
                {
                    "questionOptions": (
                        [
                            {
                                "id": question_option_item[0],
                                "content": question_option_item[1],
                                "orderInQuestion": question_option_item[2],
                            }
                            for question_option in question_options_list
                            for question_option_item in question_option
                            if question_option_item[3] == question.id
                        ]
                        if question.question_type in ["multiple_choice", "branching"]
                        else []
                    ),
                    "id": question.id,
                    "content": question.content,
                    "isDeleted": question.is_deleted,
                    "isRequired": question.is_required,
                    "orderInSection": question.order_in_section,
                    "questionType": question.question_type,
                }
                for question in questions_in_section
            ],
        }

    @classmethod
    def get_sections_in_survey(cls, process_version_version, mode=None):
        survey = Survey.check_if_survey_exists(process_version_version)
        if survey is None:
            raise Exception("Survey does not exist.")
        if (
            survey.is_published == "closed" or survey.is_published == "pending"
        ) and mode == "published":
            raise Exception("Survey is not published.")
        survey_id = survey.id
        sections_list_in_survey = Section_service.get_sections_in_survey(survey_id)
        return {
            "survey": {
                "id": survey_id,
                "name": survey.name,
                "description": survey.description,
                "allowDuplicateRespondent": survey.allow_duplicate_respondent,
            },
            "sections": sections_list_in_survey,
        }

    @classmethod
    def get_survey_response_config_some(cls, survey_id):
        try:
            survey = Survey.get_survey_response_config_some(survey_id)
            return {
                "incompleteSurveyAction": survey.incomplete_survey_action,
                "allowDuplicateRespondent": survey.allow_duplicate_respondent,
                "sendResultToRespondent": survey.send_result_to_respondent,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def publish_survey(
        cls,
        process_version_version,
        project_id,
        user_id,
        survey_url,
        email_list=None,
        start_date=None,
        end_date=None,
    ):
        try:
            # is_user_has_access = Permission_check.check_user_has_access_survey(
            #     project_id, user_id
            # )
            # if not is_user_has_access:
            #     raise Exception("User has no access to the survey")

            survey = cls.check_if_survey_exists(process_version_version)
            if survey is None:
                raise Exception("Survey does not exist.")
            survey_id = survey.id
            is_published = survey.is_published
            validation_result = cls.validate_start_date_end_date(start_date, end_date)
            if validation_result is not None:
                return validation_result
            if email_list is not None:
                cls.save_recipient_email(survey_id, email_list)
            if is_published == "closed":  # when survey is closed, publish means publish
                if start_date is None:
                    # get date and hour and minute only.
                    current_date = Date_time_convert.get_date_time_now()

                    # send survey url to the email
                    if email_list is not None:
                        for email in email_list:
                            cls.send_survey_url(
                                email, survey_url, current_date, end_date
                            )
                        # delete all emails in the database
                        Survey_send_service.delete_survey_recipient_emails(survey_id)
                    start_date = Date_time_convert.convert_string_to_date(current_date)
                    return Survey.publish_survey(
                        survey_id, start_date, end_date, survey_url, "published"
                    )

                # update end date and start date of the survey
                return Survey.publish_survey(
                    survey_id, start_date, end_date, survey_url, "pending"
                )
            elif (
                is_published == "pending"
            ):  # when survey is pending, publish means update publish status
                # only update publish status, which is email_list
                return {
                    "id": survey.id,
                    "isPublished": survey.is_published,
                    "startDate": survey.start_date,
                    "endDate": survey.end_date,
                    "surveyUrl": survey.survey_url,
                }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def send_survey_url(cls, email, survey_url, start_date=None, end_date=None):
        try:
            return Email.send_survey_url(email, survey_url, start_date, end_date)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def close_publish_survey(cls, user_id, project_id, process_version_version):
        try:
            survey = Survey.check_if_survey_exists(process_version_version)
            if survey is None:
                return {"message": "Survey does not exist."}
            # reset start date and end date to None
            cls.reset_dates(survey.id)
            return Survey.close_publish_survey(survey.id)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def save_recipient_email(cls, survey_id, email_list):
        try:
            # insert into table survey_recipient unique email
            # then insert into table send_survey with survey_id and recipient_id
            recipient_list = Survey_recipient_service.save_recipient_email(email_list)
            # update survey_recipient_association table with latest recipient list
            current_recipient_list = Survey_send_service.get_survey_recipient_email(
                survey_id
            )
            for recipient in current_recipient_list:
                Survey_send_service.delete_survey_recipient_email(
                    survey_id, recipient.id
                )

            for recipient_list_item in recipient_list:
                Survey_send_service.save_survey_recipient_email(
                    survey_id, recipient_list_item.id
                )
            return recipient_list
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_publish_info(cls, process_version_version, project_id, user_id):
        try:
            # is_user_has_access = Permission_check.check_user_has_access_survey(
            #     project_id, user_id
            # )
            # if not is_user_has_access:
            #     raise Exception("User has no access to the survey")
            survey = cls.check_if_survey_exists(process_version_version)
            if survey is None:
                return {"message": "Survey does not exist."}

            # get email list
            email_list = Survey_send_service.get_survey_recipient_email(survey.id)
            return {
                "id": survey.id,
                "email": [email.email for email in email_list],
                "surveyUrl": survey.survey_url,
                "startDate": survey.start_date,
                "endDate": survey.end_date,
                "isPublished": survey.is_published,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def set_survey_published(cls, survey_id):
        try:
            return Survey.set_survey_published(survey_id)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_unpublished_surveys(cls):
        try:
            return Survey.get_unpublished_surveys()
        except Exception as e:
            raise Exception(e)

    @classmethod
    def set_survey_closed(cls, survey_id):
        try:
            return Survey.set_survey_closed(survey_id)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_published_surveys(cls):
        try:
            return Survey.get_published_surveys()
        except Exception as e:
            raise Exception(e)

    @classmethod
    def reset_dates(cls, survey_id):
        try:
            return Survey.reset_dates(survey_id)
        except Exception as e:
            raise Exception(e)
