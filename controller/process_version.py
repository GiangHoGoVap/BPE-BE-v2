from bpsky import bpsky
from controller.utils import *


@bpsky.route(
    "/api/v1/project/<int:project_id>/process/<int:process_id>/version",
    methods=["GET", "POST", "DELETE"],
)
def process_version(project_id, process_id):
    try:
        if request.method == "GET":
            return process_version_get_by_process(project_id, process_id)
        elif request.method == "POST":
            return process_version_create_new_version(project_id, process_id)
        else:
            return process_version_delete_oldest_version(project_id, process_id)
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_version_get_by_process(project_id, process_id):
    user_id = get_id_from_token(get_token(request))
    versions = ProcessVersionService.get_by_process(user_id, project_id, process_id)
    return versions


def process_version_create_new_version(project_id, process_id):
    user_id = get_id_from_token(get_token(request))
    if "file" not in request.files:
        raise Exception("file required")
    file = request.files["file"]
    ProcessVersionService.create_new_version(user_id, file, project_id, process_id)
    return "Create successfully"


def process_version_delete_oldest_version(project_id, process_id):
    user_id = get_id_from_token(get_token(request))
    ProcessVersionService.delete_oldest_version(user_id, project_id, process_id)
    return "Delete successfully"


@bpsky.route(
    "/api/v1/project/<int:project_id>/process/<int:process_id>/version/<string:version>",
    methods=["GET", "PUT", "DELETE"],
)
def process_individual_version(project_id, process_id, version):
    try:
        if request.method == "GET":
            return process_version_get_content_by_version(
                project_id, process_id, version
            )
        elif request.method == "PUT":
            return process_version_save(project_id, process_id, version)
        else:
            return process_version_delete_version(project_id, process_id, version)
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_version_get_content_by_version(project_id, process_id, version):
    user_id = get_id_from_token(get_token(request))
    content = ProcessVersionService.get_content_by_version(
        user_id, project_id, process_id, version
    )
    return bpsky.response_class(response=content, content_type="xml", status=200)


def process_version_save(project_id, process_id, version):
    user_id = get_id_from_token(get_token(request))
    if "file" not in request.files:
        raise Exception("file required")
    file = request.files["file"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    ProcessVersionService.save(
        xml_file_link, file, user_id, project_id, process_id, version
    )
    return "Save successfully"


def process_version_delete_version(project_id, process_id, version):
    user_id = get_id_from_token(get_token(request))
    ProcessVersionService.delete_version(user_id, project_id, process_id, version)
    return "Delete successfully"


@bpsky.route("/api/v1/comment", methods=["GET", "POST", "PUT", "DELETE"])
def process_version_comment():
    try:
        if request.method == "GET":
            return process_version_get_comment_by_bpmn_file()
        elif request.method == "POST":
            return process_version_add_comment()
        elif request.method == "PUT":
            return process_version_edit_comment()
        else:
            return process_version_delete_comment()

    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_version_add_comment():
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    for i in ["projectID", "processID", "version", "content"]:
        if i not in body:
            raise Exception(i + " required")
    project_id = body["projectID"]
    process_id = body["processID"]
    version = body["version"]
    content = body["content"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    data = ProcessVersionService.comment(
        user_id, project_id, process_id, xml_file_link, content
    )
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial), content_type="json", status=200
    )


def process_version_edit_comment():
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    for i in ["projectID", "processID", "version", "id", "content"]:
        if i not in body:
            raise Exception(i + " required")
    project_id = body["projectID"]
    process_id = body["processID"]
    version = body["version"]
    id = body["id"]
    content = body["content"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    ProcessVersionService.edit_comment(
        user_id, project_id, process_id, xml_file_link, id, content
    )
    return "Edit successfully"


def process_version_delete_comment():
    user_id = get_id_from_token(get_token(request))
    body = load_request_body(request)
    for i in ["projectID", "processID", "version", "id"]:
        if i not in body:
            raise Exception(i + " required")
    project_id = body["projectID"]
    process_id = body["processID"]
    version = body["version"]
    id = body["id"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    ProcessVersionService.delete_comment(
        user_id, project_id, process_id, xml_file_link, id
    )
    return "Delete successfully"


def process_version_get_comment_by_bpmn_file():
    user_id = get_id_from_token(get_token(request))
    project_id = request.args.get("projectID", "")
    process_id = request.args.get("processID", "")
    version = request.args.get("version", "")
    if project_id == "" or version == "":
        raise Exception("projectID or processID or version required")
    xml_file_link = get_xml_link(project_id, process_id, version)
    data = ProcessVersionService.get_comment_by_bpmn_file(
        user_id, project_id, process_id, xml_file_link
    )
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial), content_type="json", status=200
    )


@bpsky.route("/api/v1/comment/user", methods=["GET"])
def process_version_get_comment_by_user():
    try:
        user_id = get_id_from_token(get_token(request))
        data = ProcessVersionService.get_comment_by_user(user_id)
        return bpsky.response_class(
            response=json.dumps(data, default=json_serial),
            content_type="json",
            status=200,
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/image", methods=["GET", "POST"])
def process_version_image():
    try:
        if request.method == "GET":
            return process_version_get_image_by_bpmn_file()
        else:
            return process_version_add_image()
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


def process_version_get_image_by_bpmn_file():
    user_id = get_id_from_token(get_token(request))
    project_id = request.args.get("projectID", "")
    version = request.args.get("version", "")
    process_id = request.args.get("processID", "")
    if project_id == "" or version == "" or process_id == "":
        raise Exception("projectID or version required")
    xml_file_link = get_xml_link(project_id, process_id, version)
    data = ImageService.get_image_by_bpmn_file(
        user_id, project_id, process_id, xml_file_link
    )
    return bpsky.response_class(
        response=json.dumps(data, default=json_serial), content_type="json", status=200
    )


def process_version_add_image():
    user_id = get_id_from_token(get_token(request))
    if "file" not in request.files:
        raise Exception("file required")
    for i in ["projectID", "processID", "version"]:
        if i not in request.form:
            raise Exception(i + " required")
    file = request.files["file"]
    project_id = request.form["projectID"]
    process_id = request.form["processID"]
    version = request.form["version"]
    xml_file_link = get_xml_link(project_id, process_id, version)
    ImageService.insert_image(user_id, project_id, process_id, xml_file_link, file)
    return "Create successfully"


@bpsky.route("/api/v1/autosave/file", methods=["PUT"])
def process_autosave_file():
    try:
        user_id = get_id_from_token(get_token(request))
        files = list(request.files.listvalues())
        if len(files) == 0:
            raise Exception("files required")
        if "data" not in request.form:
            raise Exception("data required")
        data = request.form["data"]
        ProcessVersionService.bulk_save(user_id, files[0], json.loads(data))
        return "Save successfully"
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/autosave/image", methods=["POST"])
def process_autosave_image():
    try:
        user_id = get_id_from_token(get_token(request))
        files = list(request.files.listvalues())
        if len(files) == 0:
            raise Exception("files required")
        if "data" not in request.form:
            raise Exception("data required")
        data = request.form["data"]
        ImageService.bulk_insert(user_id, files[0], json.loads(data))
        return "Save successfully"
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)
