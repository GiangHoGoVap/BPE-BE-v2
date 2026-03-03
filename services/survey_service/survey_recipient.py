from data.repositories.survey_features.survey_recipient import (
    Survey_recipient,
    Survey_send,
)


class Survey_send_service:
    @classmethod
    def save_survey_recipient_email(cls, survey_id, recipient_id):
        # get all email sent to the survey
        return Survey_send.save_survey_recipient_email(survey_id, recipient_id)

    @classmethod
    def get_survey_recipient_email(cls, survey_id):
        # get all email sent to the survey
        return Survey_send.get_survey_recipient_email(survey_id)

    @classmethod
    def delete_survey_recipient_email(cls, survey_id, recipient_id):
        # delete email sent to the survey
        return Survey_send.delete_survey_recipient_email(survey_id, recipient_id)

    @classmethod
    def get_all_emails_dates_url_of_not_published_survey(cls):
        email_and_start_date_and_url = (
            Survey_send.get_all_emails_dates_url_of_not_published_survey()
        )
        return email_and_start_date_and_url

    @classmethod
    def delete_survey_recipient_emails(cls, survey_id):
        return Survey_send.delete_survey_recipient_mails(survey_id)


class Survey_recipient_service:
    @classmethod
    def save_recipient_email(cls, email_list):
        # only insert if email does not exist
        try:
            recipient_list = []
            for email in email_list:
                # check if email exists
                existed_email = cls.check_if_email_exists(email)
                if existed_email:
                    recipient_list.append(existed_email)
                    continue
                recipient = Survey_recipient.save_recipient_email(email)
                recipient_list.append(recipient)
            return recipient_list
        except Exception as e:
            raise Exception(e)

    @classmethod
    def check_if_email_exists(cls, email):
        return Survey_recipient.check_if_email_exists(email)
