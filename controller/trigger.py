import jsonpickle

from bpsky import bpsky
from controller.utils import *


@bpsky.route("/trigger", methods=["GET"])
def trigger_server_to_stop_sleeping():
    return bpsky.response_class(
        response=jsonpickle.encode("Server is awake", unpicklable=False),
        status=200,
        mimetype="application/json",
    )
