from bpsky import bpsky
from controller.utils import *


@bpsky.route("/api/v1/result/all", methods=["GET"])
def evaluated_result_get_result_by_bpmn_file():
    try:
        user_id = get_id_from_token(get_token(request))
        project_id = request.args.get("projectID", "")
        version = request.args.get("version", "")
        process_id = request.args.get("processID", "")
        if project_id == "" or version == "" or process_id == "":
            raise Exception("projectID or version or processID required")
        xml_file_link = get_xml_link(project_id, process_id, version)
        data = EvaluatedResultService.get_all_result_by_bpmn_file(
            user_id, project_id, process_id, xml_file_link
        )
        return bpsky.response_class(
            response=json.dumps(data, default=json_serial),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/result", methods=["GET", "POST", "DELETE"])
def evaluated_result():
    try:
        if request.method == "GET":
            return evaluated_result_get()
        elif request.method == "POST":
            return evaluated_result_save()
        else:
            return evaluated_result_delete()
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def evaluated_result_save():
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    for i in ["projectID", "processID", "version", "name", "result"]:
        if i not in body:
            raise Exception(i + " required")
    project_id = body["projectID"]
    process_id = body["processID"]
    version = body["version"]
    name = body["name"]
    result = body["result"]
    description = body["description"] if "description" in body else ""
    xml_file_link = get_xml_link(project_id, process_id, version)
    EvaluatedResultService.save(
        user_id,
        xml_file_link,
        project_id,
        process_id,
        name,
        result,
        description,
        version,
    )
    return "Create successfully"


def evaluated_result_get():
    user_id = get_id_from_token(get_token(request))
    project_id = request.args.get("projectID", "")
    version = request.args.get("version", "")
    name = request.args.get("name", "")
    process_id = request.args.get("processID", "")
    if project_id == "" or version == "" or name == "" or process_id == "":
        raise Exception("projectID or version or name or processID required")
    xml_file_link = get_xml_link(project_id, process_id, version)
    data = EvaluatedResultService.get_result(
        user_id, project_id, process_id, xml_file_link, name
    )
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial),
        status=200,
        mimetype="application/json",
    )


def evaluated_result_delete():
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    for i in ["projectID", "processID", "version", "name"]:
        if i not in body:
            raise Exception(i + " required")
    project_id = body["projectID"]
    process_id = body["processID"]
    version = body["version"]
    name = body["name"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    EvaluatedResultService.delete(user_id, xml_file_link, project_id, process_id, name)
    return "Delete successfully"
