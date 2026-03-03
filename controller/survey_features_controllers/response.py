import jsonpickle
from bpsky import bpsky
from controller.utils import *
from services.survey_service.response import Response_service
from services.survey_service.survey import Survey_service
from services.survey_service.cron.scheduling import Scheduling_send_email


# @bpsky.route("/", methods=["GET"])
# def run_scheduling_send_email():
#     Scheduling_send_email.main()


@bpsky.route("/api/v1/survey/section", methods=["GET"])
def get_survey_questions_by_section_id():
    section_id = request.args.get("sectionId", None)
    data = Survey_service.get_survey_questions_by_section_id(section_id)
    return bpsky.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype="application/json",
    )


@bpsky.route("/api/v1/survey/section/all", methods=["GET"])
def get_survey_sections():
    try:
        process_version_version = request.args.get("processVersionVersion")
        mode = request.args.get("mode")
        if process_version_version is None or mode is None:
            raise Exception("params required")
        data = Survey_service.get_sections_in_survey(process_version_version, mode)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)


@bpsky.route("/api/v1/survey/submission", methods=["POST"])
def submit_survey_form():
    body = load_request_body(request)
    process_version_version = body["processVersionVersion"]
    answers = body["answers"]
    email = body["email"]
    full_name = body["fullName"]
    data = Response_service.submit_survey_form(
        answers, email, full_name, process_version_version
    )
    return bpsky.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype="application/json",
    )


@bpsky.route("/api/v1/survey/response", methods=["GET"])
def get_survey_response():
    response_id = request.args.get("responseId", None)
    data = Response_service.get_survey_response(response_id)
    return bpsky.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype="application/json",
    )
