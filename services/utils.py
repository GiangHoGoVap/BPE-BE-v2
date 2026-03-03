import hashlib
from datetime import datetime

import pytz

from data.repositories.constant import Role
from data.repositories.workspace import Workspace
from services.project_service.work_on import WorkOnService

mySalt = "$2b$12$6rMnsklapuHBKL."


def hash_password(password: str):
    pwd_hash = hashlib.sha256((password + mySalt).encode("utf-8"))
    return pwd_hash.hexdigest()


class PermissionConverter:
    @classmethod
    def convert_permission_to_role(cls, permission):
        if permission == "viewer":
            return Role.CAN_VIEW.value
        elif permission == "sharer":
            return Role.CAN_SHARE.value
        elif permission == "editor":
            return Role.CAN_EDIT.value
        else:
            return Role.OWNER.value

    @classmethod
    def convert_role_to_permission(cls, role):
        if role == Role.CAN_VIEW.value:
            return "viewer"
        elif role == Role.CAN_SHARE.value:
            return "sharer"
        elif role == Role.CAN_EDIT.value:
            return "editor"
        else:
            return "owner"

    @classmethod
    def compare_permission(
        cls, user_id_and_project_roles_list, member_id_and_workspace_permission_list
    ):
        # each parameter is a dict with 2 keys: user_id and role, each key is a list
        # return true if all user_id in user_id_and_project_roles_list has role that is higher or equal to in
        # member_id_and_workspace_permission_list
        for user in user_id_and_project_roles_list:
            for member in member_id_and_workspace_permission_list:
                if user["user_id"] == member["user_id"]:
                    if user["role"] > PermissionConverter.convert_permission_to_role(
                        member["permission"]
                    ):
                        return False

        return True


class Permission_check:
    @classmethod
    def check_user_has_access_survey(cls, project_id, user_id):
        return WorkOnService.is_project_owner(user_id, project_id)

    @classmethod
    def check_if_user_is_workspace_owner(cls, workspace_id, user_id):
        return Workspace.check_if_user_is_workspace_owner(workspace_id, user_id)


class Date_time_convert:
    @classmethod
    def convert_string_to_date(cls, date_str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

    @classmethod
    def get_date_time_now(cls) -> str:
        current_datetime = datetime.now()

        # Convert the datetime to another timezone (e.g., GMT+7)
        gmt7_timezone = pytz.timezone("Etc/GMT-7")
        datetime_in_gmt7 = current_datetime.astimezone(gmt7_timezone)

        # Format the datetime in the desired format
        formatted_datetime = datetime_in_gmt7.strftime("%Y-%m-%dT%H:%M")
        print("formatted_datetime", formatted_datetime)
        return formatted_datetime

    @classmethod
    def get_date_time_now_date(cls) -> datetime:
        now = cls.get_date_time_now()
        return cls.convert_string_to_date(now)


class Process_version_default_values:
    current_cycle_time = 0
    current_cycle_cost = 0
    current_cycle_quality = 0
    current_cycle_flexibility = 0
    health = None
    strategic_importance = None
    feasibility = None

    def __init__(self):
        pass


class Workspace_default_values:
    targeted_cycle_time = 0
    worst_cycle_time = None
    targeted_cost = 0
    worst_cost = None
    targeted_quality = 1
    worst_quality = 0
    targeted_flexibility = 1
    worst_flexibility = 0

    def __init__(self):
        pass
