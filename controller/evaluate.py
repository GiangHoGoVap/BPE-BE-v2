from bpsky import bpsky
from controller.utils import *


@bpsky.route("/api/v1/evaluate", methods=["POST"])
def evaluate_evaluate():
    try:
        body = load_request_body(request)
        result = Evaluate.evaluate(body)
        json_response = [r.__dict__ for r in result]
        return bpsky.response_class(
            response=json.dumps(json_response), status=200, mimetype="application/json"
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/evaluate/compare", methods=["POST"])
def evaluate_compare():
    try:
        body = load_request_body(request)
        result = Compare.compare(body)
        json_response = result.__dict__
        return bpsky.response_class(
            response=json.dumps(json_response), status=200, mimetype="application/json"
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)
