import os
import ssl
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email:
    @classmethod
    def send(cls, sender_email, password, receiver_email, subject, content):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        part = MIMEText(content, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    @classmethod
    def verify_account(cls, receiver_email, name, token):
        sender_email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")
        current_env = os.environ.get("FLASK_ENV")
        if current_env == "development":
            host = os.environ.get("HOST_BE")
        else:
            host = os.environ.get("HOST_BE_PROD")
        subject = "Verify your email"
        # Create the plain-text and HTML version of your message
        html = f"""\
        <html>
        <body>
            <p>Hi {name},<br>
            Please click <a href="{host}/api/v1/user/verify/{token}">here</a> to verify your account or access this bellow link:<br>
            [{host}/api/v1/user/verify/{token}]<br>
            Thank you so much,<br>
            BPSky
            </p>
        </body>
        </html>
        """
        cls.send(sender_email, password, receiver_email, subject, html)

    @classmethod
    def reset_password(cls, receiver_email, name, token):
        sender_email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")
        host = os.environ.get("HOST")
        subject = "Reset password"

        # Create the plain-text and HTML version of your message
        html = f"""\
        <html>
        <body>
            <p>Hi {name},<br>
            Please click <a href="{host}/reset-password?token={token}">here</a> to reset password or access this bellow link:<br>
            [{host}/reset-password?token={token}]<br>
            Thank you so much,<br>
            BPSky
            </p>
        </body>
        </html>
        """
        cls.send(sender_email, password, receiver_email, subject, html)

    @classmethod
    def send_survey_url(
        cls, receiver_email, survey_url, start_date=None, end_date=None
    ):
        sender_email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")
        subject = "Survey URL"

        # Create the plain-text and HTML version of your message
        html = f"""\
        <html>
        <body>
            <p>Hi there,</p>
            <p>Please click <a href="{survey_url}">here</a> to access the survey or access this bellow link:<br>
            [{survey_url}]</p>
            <p>Start date: {start_date}</p>
            {f"<p>End date: {end_date}</p>" if end_date else ""}
            <p>Thank you so much,<br>
            BPSky
            </p>
        </body>
        </html>
        """
        cls.send(sender_email, password, receiver_email, subject, html)

    @classmethod
    def send_survey_result(cls):
        pass
