from data.repositories.utils import *


class User:
    id = 0
    password = ""
    email = ""
    name = ""
    phone = ""
    avatar = ""
    verified = False

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)

    # def __init__(self, **kwargs):
    #     for arg in ["id", "password", "email", "name", "phone", "avatar", "verified"]:
    #         value = kwargs.pop(arg, None)
    #         setattr(self, arg, value)

    #     if kwargs:
    #         invalid_args = ", ".join(kwargs)
    #         raise ValueError("Invalid keyword argument(s): %s" %
    #                          (invalid_args,))

    @classmethod
    def getUserName(cls, userId):
        query = """SELECT name
                    FROM public.bpe_user
                    WHERE id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (userId,))
                result = cursor.fetchone()
                return result[0]
        except Exception as e:
            raise Exception(e)

    @classmethod
    def create(cls, hash_password, email, name, phone, avatar, verified=False):
        query = """INSERT INTO public.bpe_user
                ("password", email, "name", phone, avatar, verified)
                VALUES(%s, %s, %s, %s, %s, %s)
                RETURNING id, "password", email, "name", phone, avatar, verified;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        hash_password,
                        email,
                        name,
                        phone,
                        avatar,
                        str(verified),
                    ),
                )
                connection.commit()
                result = cursor.fetchone()
                return User(id=result[0], email=result[2], password=result[1])
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def change_password(cls, email, new_hash_password):
        query = """UPDATE public.bpe_user
                    SET "password"=%s
                    WHERE email=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        new_hash_password,
                        email,
                    ),
                )
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def verify(cls, email):
        query = """UPDATE public.bpe_user
                    SET verified=true
                    WHERE email=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                # updated_row = cursor.rowcount
                # if updated_row == 0:
                #     raise Exception("Email doesn't exist")
                connection.commit()
                return "Verify successfully"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def verify_token(cls, id, email, hash_password):
        query = """SELECT id
                    FROM public.bpe_user
                    WHERE email=%s and id=%s and password=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        email,
                        id,
                        hash_password,
                    ),
                )
                cursor.fetchone()
                return "Verify successfully"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_email(cls, email):
        query = """SELECT id, email, password, verified
                    FROM public.bpe_user
                    WHERE email=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                if result is None:
                    raise Exception("Email is incorrect")
                if result[-1]:
                    raise Exception("Your account was verified")
                return User(id=result[0], email=result[1], password=result[2])
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_email_permanently(cls, email):
        query = """SELECT id, email, password
                    FROM public.bpe_user
                    WHERE email=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                if result is None:
                    raise Exception("Email is incorrect")
                return User(id=result[0], email=result[1], password=result[2])
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get(cls, email, hash_password):
        query = """SELECT id, email, password, verified
                    FROM public.bpe_user
                    WHERE email=%s and password=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        email,
                        hash_password,
                    ),
                )
                result = cursor.fetchone()
                if result is None:
                    raise Exception("Email or password is incorrect")
                if not result[-1]:
                    raise Exception("Your account has not been verified")
                return User(id=result[0], email=result[1], password=result[2])
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_all(cls):
        query = """SELECT id, email, "name", phone, avatar
                    FROM public.bpe_user;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    ["id", "email", "name", "phone", "avatar"], result
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_id(cls, id, workspaceId=None):
        if workspaceId:
            query = f"""SELECT u.id, u.email, u.name, u.phone, u.avatar, jw.permission
                        FROM public.join_workspace jw, public.bpe_user u
                        WHERE jw.workspaceId={workspaceId} and u.id={id} and jw.memberId=u.id and jw.isDeleted=false;
                    """
        else:
            query = f"""SELECT id, email, "name", phone, avatar
                        FROM public.bpe_user
                        WHERE id= {id};
                    """

        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                # cursor.execute(query, (id,))
                cursor.execute(query)
                result = cursor.fetchone()
                if result is None:
                    raise Exception("User not found")
                if len(result) == 6:
                    return {
                        "id": result[0],
                        "email": result[1],
                        "name": result[2],
                        "phone": result[3],
                        "avatar": result[4],
                        "permission": result[5] if len(result) == 6 else None,
                    }
                return {
                    "id": result[0],
                    "email": result[1],
                    "name": result[2],
                    "phone": result[3],
                    "avatar": result[4],
                }
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_many(cls, user_ids):
        query = f"""SELECT name, phone, avatar
                    FROM public.bpe_user
                    WHERE id IN ({",".join(str(user_id) for user_id in user_ids)});
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(("name", "phone", "avatar"), result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def check_exist(cls, email):
        query = """SELECT id
                    FROM public.bpe_user
                    WHERE email=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def search(cls, s, email, workspaceId=None):
        # search user in the whole system
        # return users in workspace and users not in workspace
        # if users in workspace, return their permission
        # if workspaceId is None, return all users
        query = f"""SELECT id, email, name, phone, avatar
                    FROM public.bpe_user
                    WHERE email LIKE '%{s}%' AND email!='{email}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                if len(result) == 0:
                    return []
                if workspaceId is None:
                    return [
                        {
                            "id": user[0],
                            "email": user[1],
                            "name": user[2],
                            "phone": user[3],
                            "avatar": user[4],
                        }
                        for user in result
                    ]
                else:
                    # if workspaceId is note None, return all users in system, but with users in workspace,
                    # return including their permission
                    query = f"""SELECT u.id, u.email, u.name, u.phone, u.avatar, jw.permission
                                FROM public.join_workspace jw, public.bpe_user u
                                WHERE jw.workspaceId='{workspaceId}' and u.email != '{email}' and u.id=jw.memberId 
                                and jw.isDeleted=false;
                            """
                    cursor.execute(
                        query,
                        (
                            workspaceId,
                            ",".join(str(user[0]) for user in result),
                        ),
                    )
                    resultWithWorkspaceId = cursor.fetchall()
                    # combine 2 list, remove item with duplicate id
                    result = result + resultWithWorkspaceId
                    result = list(
                        {user[0]: user for user in result}.values()
                    )  # remove duplicate
                    return [
                        {
                            "id": user[0],
                            "email": user[1],
                            "name": user[2],
                            "phone": user[3],
                            "avatar": user[4],
                            "permission": user[5] if len(user) == 6 else None,
                        }
                        for user in result
                    ]

        except Exception as e:
            connection.rollback()
            raise Exception(e)
