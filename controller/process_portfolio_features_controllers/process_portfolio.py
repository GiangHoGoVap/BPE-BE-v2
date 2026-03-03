import jsonpickle

from bpsky import bpsky
from controller.decorators import permission_workspace_check
from controller.utils import *
from services.process_portfolio_service.feasibility import Feasibility_service
from services.process_portfolio_service.health import Health_service
from services.process_portfolio_service.process_portfolio import (
    Process_portfolio_service,
)
from services.process_portfolio_service.strategic_importance import (
    Strategic_importance_service,
)


@bpsky.route("/api/v1/workspace/portfolio/projects", methods=["GET"])
@permission_workspace_check
def get_all_projects_in_workspace():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = ProjectService.get_all_projects_in_workspace(
            workspace_id, user_id, page, limit
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/processes", methods=["GET"])
@permission_workspace_check
def get_all_processes_in_project():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        project_id = request.args.get("projectId")
        data = ProcessService.get_all_processes_in_project(
            workspace_id, project_id, user_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/processversion", methods=["GET"])
@permission_workspace_check
def get_all_process_versions_in_process():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        process_id = request.args.get("processId")
        data = ProcessVersionService.get_all_process_versions_in_process(
            workspace_id, process_id, user_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/processversion/activation", methods=["POST"])
@permission_workspace_check
def activate_process_version():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        workspace_id = body["workspaceId"]
        process_version_version = body["processVersionVersion"]
        process_id = body["processId"]
        data = ProcessVersionService.activate_process_version(
            user_id, workspace_id, process_version_version, process_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/measurements", methods=["GET"])
@permission_workspace_check
def get_workspace_measurements():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        data = WorkspaceService.get_workspace_measurements(workspace_id, user_id)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/measurements", methods=["PUT"])
@permission_workspace_check
def edit_workspace_measurements():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        workspace_id = body["workspaceId"]
        targeted_cycle_time = (
            body["targetedCycleTime"] if "targetedCycleTime" in body else None
        )
        worst_cycle_time = body["worstCycleTime"] if "worstCycleTime" in body else None
        targeted_cost = body["targetedCost"] if "targetedCost" in body else None
        worst_cost = body["worstCost"] if "worstCost" in body else None
        targeted_quality = (
            body["targetedQuality"] if "targetedQuality" in body else None
        )
        worst_quality = body["worstQuality"] if "worstQuality" in body else None
        targeted_flexibility = (
            body["targetedFlexibility"] if "targetedFlexibility" in body else None
        )
        worst_flexibility = (
            body["worstFlexibility"] if "worstFlexibility" in body else None
        )
        data = WorkspaceService.edit_workspace_measurements(
            workspace_id,
            user_id,
            targeted_cycle_time,
            worst_cycle_time,
            targeted_cost,
            worst_cost,
            targeted_quality,
            worst_quality,
            targeted_flexibility,
            worst_flexibility,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/processversion/measurements", methods=["GET"])
@permission_workspace_check
def get_measurements_of_process_versions():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        process_version_version = request.args.get("processVersionVersion")
        data = Process_portfolio_service.get_measurements_of_process_version(
            workspace_id, user_id, process_version_version
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route(
    "/api/v1/workspace/portfolio/processversion/measurements", methods=["POST"]
)
@permission_workspace_check
def edit_measurements_of_active_process_version():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        workspace_id = body["workspaceId"]
        process_version_version = body["processVersionVersion"]

        current_cycle_time = (
            body["currentCycleTime"] if "currentCycleTime" in body else None
        )

        current_cost = body["currentCost"] if "currentCost" in body else None

        current_quality = body["currentQuality"] if "currentQuality" in body else None

        current_flexibility = (
            body["currentFlexibility"] if "currentFlexibility" in body else None
        )

        strategic_importance = (
            body["strategicImportance"] if "strategicImportance" in body else None
        )
        feasibility = body["feasibility"] if "feasibility" in body else None

        data = Process_portfolio_service.edit_measurements_of_process_version(
            workspace_id,
            process_version_version,
            user_id,
            current_cycle_time,
            current_cost,
            current_quality,
            current_flexibility,
            strategic_importance,
            feasibility,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/feasibility", methods=["POST"])
@permission_workspace_check
def edit_feasibility_of_active_process_version():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        workspace_id = body["workspaceId"]
        process_version_version = body["processVersionVersion"]
        total_score = body["totalScore"]
        data = Feasibility_service.edit_feasibility_of_process_versions(
            workspace_id, process_version_version, user_id, total_score
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/strategic_importance", methods=["POST"])
@permission_workspace_check
def edit_strategic_importance_of_active_process_version():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        workspace_id = body["workspaceId"]
        process_version_version = body["processVersionVersion"]
        total_score = body["totalScore"]
        data = (
            Strategic_importance_service.edit_strategic_importance_of_process_version(
                workspace_id, process_version_version, user_id, total_score
            )
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


# @bpsky.route("/api/v1/workspace/portfolio", methods=["POST"])
# def create_process_portfolio():
#     try:
#         user_id = get_id_from_token(get_token(request))
#         body = load_request_body(request)
#         workspace_id = body["workspaceId"]
#         data = Process_portfolio_service.create_process_portfolio(workspace_id, user_id)
#         return bpsky.response_class(
#             response=jsonpickle.encode(data, unpicklable=False),
#             status=200,
#             mimetype="application/json",
#         )
#     except Exception as e:
#         return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio", methods=["GET"])
@permission_workspace_check
def get_process_portfolio_content():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        data = Process_portfolio_service.get_process_portfolio_content(
            workspace_id, user_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/workspace/portfolio/processversion/notavailable", methods=["GET"])
@permission_workspace_check
def get_not_available_process_versions():
    try:
        user_id = get_id_from_token(get_token(request))
        workspace_id = request.args.get("workspaceId")
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = Process_portfolio_service.get_not_available_process_versions(
            workspace_id, user_id, page, limit
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)
