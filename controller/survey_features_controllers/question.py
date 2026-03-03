import jsonpickle

from bpsky import bpsky
from controller.decorators import permission_project_check
from controller.utils import *
from services.survey_service.question import Question_service
from services.survey_service.question_in_section import Question_in_section_service


@bpsky.route("/api/v1/survey/question", methods=["GET"])
@permission_project_check
def get_question_detail_in_survey():
    try:
        user_id = get_id_from_token(get_token(request))
        project_id = request.args.get("projectId", None)
        question_in_section_id = request.args.get("questionInSectionId", None)
        data = Question_in_section_service.get_question_detail_in_survey(
            question_in_section_id, project_id, user_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/question", methods=["PUT"])
@permission_project_check
def update_question_detail_in_survey():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        content = body["content"] if "content" in body else None
        question_type = body["questionType"] if "questionType" in body else None
        is_required = body["isRequired"] if "isRequired" in body else None
        order_in_section = body["orderInSection"] if "orderInSection" in body else None
        question_options = (
            body["questionOptions"] if "questionOptions" in body else None
        )
        project_id = body["projectId"]
        weight = body["weight"] if "weight" in body else None
        question_in_section_id = body["questionInSectionId"]
        section_id = body["sectionId"]
        data = Question_in_section_service.update_question_detail_in_survey(
            user_id,
            project_id,
            section_id,
            question_in_section_id,
            question_type,
            is_required,
            order_in_section,
            weight,
            content,
            question_options,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/init", methods=["POST"])
@permission_project_check
def initialize_sample_questions():
    try:
        user_id = get_id_from_token(get_token(request))
        data = Question_service.initialize_sample_questions()
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/question", methods=["DELETE"])
@permission_project_check
def delete_question_in_survey():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        project_id = body["projectId"]
        question_in_section_id = body["questionInSectionId"]
        section_id = body["sectionId"]
        data = Question_in_section_service.delete_question_in_survey(
            user_id, project_id, section_id, question_in_section_id
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/question/contribution", methods=["POST"])
@permission_project_check
def contribute_question_in_survey():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        project_id = body["projectId"]
        survey_domain = body["surveyDomain"]
        section_id = body["sectionId"]
        is_required = body["isRequired"]
        order_in_section = body["orderInSection"]
        weight = body["weight"]
        content = body["content"]
        question_type = body["questionType"]
        content = body["content"]
        question_id = body["questionId"]
        question_in_section_id = body["questionInSectionId"]
        question_options = (
            body["questionOptions"] if "questionOptions" in body else None
        )
        data = Question_in_section_service.contribute_question(
            user_id,
            project_id,
            survey_domain,
            section_id,
            question_id,
            question_in_section_id,
            question_type,
            is_required,
            order_in_section,
            weight,
            content,
            question_options,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/question", methods=["POST"])
@permission_project_check
def create_new_question_in_survey():
    try:
        user_id = get_id_from_token(get_token(request))
        body = load_request_body(request)
        project_id = body["projectId"]
        question_type = body["questionType"]
        content = body["content"]
        section_id = body["sectionId"]
        order_in_section = body["orderInSection"]
        weight = body["weight"] if "weight" in body else 1
        is_required = body["isRequired"] if "isRequired" in body else False
        question_options = (
            body["questionOptions"] if "questionOptions" in body else None
        )
        data = Question_in_section_service.add_new_question_to_section(
            user_id,
            project_id,
            section_id,
            content,
            order_in_section,
            weight,
            is_required,
            question_type,
            question_options,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )


@bpsky.route("/api/v1/survey/question/suggestion", methods=["GET"])
@permission_project_check
def get_question_suggestion():
    try:
        user_id = get_id_from_token(get_token(request))
        project_id = request.args.get("projectId", None)
        data = Question_service.get_all_questions(project_id, user_id)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(
            response=jsonpickle.encode(str(e), unpicklable=False),
            status=500,
            mimetype="application/json",
        )
