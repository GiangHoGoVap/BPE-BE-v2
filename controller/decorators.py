from functools import wraps

import jsonpickle
from flask import request

from bpsky import bpsky
from controller.utils import get_id_from_token, get_token, load_request_body
from exceptions import AccessNotAllowed, WorkspaceNotFound, CustomException
from services.utils import Permission_check


def permission_project_check(func):
    @wraps(func)
    def decorator_function(*args, **kwargs):
        try:
            user_id = get_id_from_token(get_token(request))
            if request.method == "GET":
                project_id = request.args.get("projectId")
            else:
                body = load_request_body(request)
                project_id = body["projectId"]

            if project_id is None or str(project_id).strip() in {
                "",
                "undefined",
                "null",
            }:
                return bpsky.response_class(
                    jsonpickle.encode({"message": "projectId is required"}),
                    status=400,
                    mimetype="application/json",
                )

            try:
                project_id = int(project_id)
            except (TypeError, ValueError):
                return bpsky.response_class(
                    jsonpickle.encode({"message": "projectId must be an integer"}),
                    status=400,
                    mimetype="application/json",
                )

            if not Permission_check.check_user_has_access_survey(project_id, user_id):
                raise AccessNotAllowed("User does not have access to this survey")
            return func(*args, **kwargs)
        except CustomException as e:
            return bpsky.response_class(e.__str__(), status=e.status_code)
        except Exception as e:
            return bpsky.response_class(
                jsonpickle.encode({"message": str(e)}),
                status=500,
                mimetype="application/json",
            )

    return decorator_function


def permission_workspace_check(func):
    @wraps(func)
    def decorator_function(*args, **kwargs):
        try:
            user_id = get_id_from_token(get_token(request))
            if request.method == "GET":
                workspace_id = request.args.get("workspaceId")
            else:
                body = load_request_body(request)
                workspace_id = body["workspaceId"]
            check = Permission_check.check_if_user_is_workspace_owner(
                workspace_id, user_id
            )
            if check is False:
                raise AccessNotAllowed("User does not have access to this workspace")
            elif check == "Workspace not found":
                raise WorkspaceNotFound("Workspace not found")
            return func(*args, **kwargs)
        except CustomException as e:
            return bpsky.response_class(e.__str__(), status=e.status_code)

    return decorator_function
