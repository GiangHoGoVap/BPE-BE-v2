import os
import requests
import json
from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", None)
GOOGLE_REDIRECT_URI_PROD = os.environ.get("GOOGLE_REDIRECT_URI_PROD", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
ENV = os.environ.get("FLASK_ENV", None)
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


class LoginWithGoogle:
    @classmethod
    def login(cls):
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        print("env", ENV)
        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        if ENV == "development":
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=GOOGLE_REDIRECT_URI,
                scope=["openid", "email", "profile"],
            )
        else:
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=GOOGLE_REDIRECT_URI_PROD,
                scope=["openid", "email", "profile"],
            )
        return request_uri

    @classmethod
    def get(cls, request_url, code):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        print("env", ENV)
        if ENV == "development":
            token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request_url,
            # authorization_response="http://localhost:5173",
            redirect_url=GOOGLE_REDIRECT_URI,
            code=code,
        )
        else:
            token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request_url,
            # authorization_response="http://localhost:5173",
            redirect_url=GOOGLE_REDIRECT_URI_PROD,
            code=code,
        )

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)

        userinfo_response = requests.get(uri, headers=headers, data=body)
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]

        else:
            raise Exception("User email not available or not verified by Google.")
        return [unique_id, users_email, picture, users_name]
