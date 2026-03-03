from bpsky import bpsky
from controller.utils import *


@bpsky.route("/api/v1/project/<int:project_id>/process", methods=["GET", "POST"])
def process_project(project_id):
    try:
        if request.method == "GET":
            return process_get_by_project(project_id)
        else:
            return process_create(project_id)

    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_create(project_id):
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    if "name" not in body:
        raise Exception("name required")
    name = body["name"]
    data = ProcessService.create(user_id, project_id, name).__dict__
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial),
        status=200,
        mimetype="application/json",
    )


def process_get_by_project(project_id):
    user_id = get_id_from_token(get_token(request))
    data = ProcessService.get_by_project(user_id, project_id)
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial),
        status=200,
        mimetype="application/json",
    )


@bpsky.route(
    "/api/v1/project/<int:project_id>/process/<int:process_id>",
    methods=["PUT", "DELETE"],
)
def process_process(project_id, process_id):
    try:
        if request.method == "PUT":
            return process_update_name(project_id, process_id)
        else:
            return process_delete_process(project_id, process_id)
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_update_name(project_id, process_id):
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    if "name" not in body:
        raise Exception("name required")
    name = body["name"]
    ProcessService.update_name(user_id, project_id, process_id, name)
    return "Update successfully"


def process_delete_process(project_id, process_id):
    user_id = get_id_from_token(get_token(request))
    ProcessService.delete(user_id, project_id, process_id)
    return "Delete successfully"
