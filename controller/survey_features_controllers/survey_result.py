import jsonpickle

from bpsky import bpsky
from controller.utils import *
from services.survey_service.survey_result import Survey_result_service


@bpsky.route("/api/v1/survey/result", methods=["GET"])
def get_survey_result():
    process_version_version = request.args.get("processVersionVersion", None)
    data = Survey_result_service.get_survey_result(process_version_version)
    return bpsky.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype="application/json",
    )


@bpsky.route("/api/v1/survey/answer", methods=["GET"])
def get_answer_details():
    process_version_version = request.args.get("processVersionVersion", None)
    data = Survey_result_service.get_answer_details(process_version_version)
    return bpsky.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype="application/json",
    )
