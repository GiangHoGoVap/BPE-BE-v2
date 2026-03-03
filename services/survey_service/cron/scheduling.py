import time
from datetime import datetime

import schedule

from bpsky import bpsky
from services.survey_service.survey import Survey_service
from services.survey_service.survey_recipient import Survey_send_service
from services.utils import Date_time_convert
from smtp.email import Email
import threading


class Scheduling_send_email:
    emails_dates_url = None

    @classmethod
    def get_email_recipients_and_survey_url(cls):
        emails_and_start_date_and_url = (
            Survey_send_service.get_all_emails_dates_url_of_not_published_survey()
        )
        cls.emails_dates_url = emails_and_start_date_and_url

    @classmethod
    def send_email(cls, email, survey_url, start_date, end_date):
        print("sending email")
        Email.send_survey_url(email, survey_url, start_date, end_date)
        print("email sent")

    @classmethod
    def get_unpublished_surveys(cls):
        return Survey_service.get_unpublished_surveys()

    @classmethod
    def schedule_emails(cls):
        try:
            with bpsky.app_context():
                cls.get_email_recipients_and_survey_url()
                # if no email but start date comes, then set publish survey

                for item in cls.emails_dates_url[:]:
                    email = item.email
                    survey_url = item.survey_url
                    start_date = item.start_date
                    end_date = item.end_date
                    survey_id = item.id
                    recipient_id = item.recipient_id
                    current = Date_time_convert.get_date_time_now_date()

                    if current == start_date and current.time() == start_date.time():
                        cls.send_email(email, survey_url, start_date, end_date)
                        # which email has been sent, remove it in database
                        Survey_send_service.delete_survey_recipient_email(
                            survey_id, recipient_id
                        )
                        # get all remaining emails of the survey, if there is no email left, set survey to published
                        remaining_emails = cls.get_remaining_emails_of_survey(survey_id)
                        if len(remaining_emails) == 0:
                            published_survey = Survey_service.set_survey_published(
                                survey_id
                            )
                            print("survey published", published_survey)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def schedule_publish_survey(cls):
        # if survey has no emails to send, but start date comes, then set survey to published
        try:
            with bpsky.app_context():
                unpublished_surveys = cls.get_unpublished_surveys()
                for survey in unpublished_surveys:
                    survey_id = survey.id
                    start_date = survey.start_date
                    current = Date_time_convert.get_date_time_now_date()
                    # print("current scheduling", current, start_date)
                    # print(len(cls.get_remaining_emails_of_survey(survey_id)))
                    # check if survey has no emails to send
                    if len(cls.get_remaining_emails_of_survey(survey_id)) == 0:
                        # print(current == start_date, current.time() == start_date.time())
                        if (
                            current == start_date
                            and current.time() == start_date.time()
                        ):
                            published_survey = Survey_service.set_survey_published(
                                survey_id
                            )
                            print("survey published", published_survey)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def schedule_close_survey(cls):
        with bpsky.app_context():
            # get all surveys that are published
            published_surveys = Survey_service.get_published_surveys()
            for survey in published_surveys:
                survey_id = survey.id
                end_date = survey.end_date
                current = Date_time_convert.get_date_time_now_date()
                if current == end_date and current.time() == end_date.time():
                    closed_survey = Survey_service.set_survey_closed(survey_id)
                    # reset dates
                    Survey_service.reset_dates(survey_id)
                    print("survey closed", closed_survey)

    @classmethod
    def schedule_loop_send_emails_and_publish_survey(cls):
        try:
            while True:
                print("schedule running")
                cls.schedule_publish_survey()
                cls.schedule_emails()
                schedule.run_pending()
                time.sleep(40)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def schedule_loop_close_survey(cls):
        try:
            while True:
                print("schedule close survey running")
                cls.schedule_close_survey()
                schedule.run_pending()
                time.sleep(60)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_remaining_emails_of_survey(cls, survey_id):
        emails_and_start_date_and_url = (
            Survey_send_service.get_all_emails_dates_url_of_not_published_survey()
        )
        return [item for item in emails_and_start_date_and_url if item.id == survey_id]
