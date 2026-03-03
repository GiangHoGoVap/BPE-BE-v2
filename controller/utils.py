from datetime import date, datetime
from auth.jwt import *
from bpsky import bpsky
from flask import request, redirect
from services.evaluate.evaluate import Evaluate
from services.evaluate.compare import Compare
from services.project_service.project import ProjectService
from services.user_service.user import UserService
from services.process_service.process_version import ProcessVersionService
from services.process_service.process import ProcessService
from services.file_service.evaluate_result import EvaluatedResultService
from services.file_service.image import ImageService
from services.workspace_service.workspace import WorkspaceService
from services.workspace_service.join_workspace import JoinWorkspaceService
from services.request_service.request import RequestService
from services.notification_service.notification import NotificationService
from services.workspace_service.join_workspace import CheckPermission
from bpsky import socketio
import json


def load_request_body(request):
    try:
        body = request.get_json()
    except Exception as e:
        raise Exception("body required")
    return body


def get_token(request):
    if "Authorization" in request.headers:
        return request.headers["Authorization"].split()[1]

    raise Exception("invalid token")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_xml_link(project_id, process_id, version):
    return f"static/{project_id}/{process_id}/{version}.bpmn"
