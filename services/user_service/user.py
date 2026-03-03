from data.repositories.user import User
from smtp.email import Email
from threading import Thread
import uuid
from auth.jwt import encode
from services.utils import *


class UserService:
    @classmethod
    def create(cls, password, email, name, phone, avatar, verified=False):
        return User.create(
            hash_password(password), email, name, phone, avatar, verified
        )

    @classmethod
    def signin(cls, email, password):
        result = User.get(email, hash_password(password))
        print(
            encode(
                {"id": result.id, "email": result.email, "password": result.password}
            )
        )
        return encode(
            {"id": result.id, "email": result.email, "password": result.password}
        )

    @classmethod
    def signup(cls, password, email, name, phone, avatar):
        if not UserService.check_exist(email):
            result = UserService.create(password, email, name, phone, avatar)
            Thread(
                target=Email.verify_account,
                args=(
                    email,
                    name,
                    encode({"id": result.id, "email": email, "password": password}),
                ),
            ).start()
            return {
                "id": result.id,
                "email": result.email,
                "name": result.name,
            }
        else:
            return "Account exist"

    @classmethod
    def verify_token(cls, user_id, email, password):
        User.verify_token(user_id, email, hash_password(password))

    @classmethod
    def resend_email(cls, email):
        user = User.get_by_email(email)
        Thread(
            target=Email.verify_account,
            args=(
                email,
                user.name,
                encode({"id": user.id, "email": email, "password": user.password}),
            ),
        ).start()
        return "Resend successfully"

    @classmethod
    def change_password(cls, email, new_password):
        User.change_password(email, hash_password(new_password))

    @classmethod
    def reset_password(cls, email):
        user = User.get_by_email_permanently(email)
        Thread(
            target=Email.reset_password,
            args=(
                email,
                user.name,
                encode({"id": user.id, "email": email, "password": user.password}),
            ),
        ).start()

    @classmethod
    def verify(cls, email):
        user = User.verify(email)
        return user

    @classmethod
    def get(cls, user_id, workspaceId=None):
        user = User.get_by_id(user_id, workspaceId)
        return user

    @classmethod
    def get_all(cls):
        return User.get_all()

    @classmethod
    def get_many(cls, user_ids):
        return User.get_many(user_ids)

    @classmethod
    def check_exist(cls, email):
        return User.check_exist(email)

    @classmethod
    def search(cls, s, email, workspaceId=None):
        return User.search(s, email, workspaceId)

    @classmethod
    def auth_with_google(cls, email, picture, name):
        if cls.check_exist(email):
            User.verify(email)
            result = User.get_by_email_permanently(email)
        else:
            password = str(uuid.uuid1())[:10]
            result = cls.create(hash_password(password), email, name, "", picture, True)
        return encode(
            {"id": result.id, "email": result.email, "password": result.password}
        )
