import jwt
import os
from data.repositories.user import User
from exceptions import InvalidToken


def encode(payload):
    return jwt.encode(payload, os.environ.get("SECRET"), algorithm="HS256")


def decode(jwt_string):
    try:
        return jwt.decode(jwt_string, os.environ.get("SECRET"), algorithms=["HS256"])
    except Exception:
        raise InvalidToken()


def verify_token(inp):
    for i in ["id", "email", "password"]:
        if i not in inp:
            raise Exception("token invalid")
    print(inp)
    id = inp["id"]
    email = inp["email"]
    password = inp["password"]
    User.verify_token(id, email, password)


def get_id_from_token(jwt_string):
    try:
        result = jwt.decode(jwt_string, os.environ.get("SECRET"), algorithms=["HS256"])
        verify_token(result)
        return result["id"]
    except Exception:
        raise InvalidToken()


def get_email_from_token(jwt_string):
    try:
        result = jwt.decode(jwt_string, os.environ.get("SECRET"), algorithms=["HS256"])
        verify_token(result)
        return result["email"]
    except Exception:
        raise InvalidToken()
