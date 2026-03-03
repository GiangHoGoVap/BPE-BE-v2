from controller.utils import *
import jsonpickle


@bpsky.route("/api/v1/request", methods=["GET"])
def getAllRequests():
    try:
        workspaceId = request.args.get("workspaceId")
        keyword = request.args.get("keyword", None)
        request_type = request.args.get("type", None)
        status = request.args.get("status", None)
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = RequestService.getAllRequests(
            workspaceId, page, limit, keyword, request_type, status
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)


@bpsky.route("/api/v1/request", methods=["POST"])
def insertNewRequest():
    try:
        body = load_request_body(request)
        handlerId = get_id_from_token(get_token(request))
        requestType = body["requestType"]
        content = body["content"]
        createdAt = datetime.now()
        status = "pending"
        workspaceId = body["workspaceId"]
        senderId = body["senderId"]
        recipientId = body["recipientId"]
        fr_permission = body["frPermission"] if "frPermission" in body else ""
        to_permission = body["toPermission"] if "toPermission" in body else ""
        rcp_permission = body["rcpPermission"] if "rcpPermission" in body else ""
        if fr_permission == "" and to_permission == "" and rcp_permission == "":
            raise Exception("No permission is set")

        checkSenderPermission = CheckPermission.checkMemberPermission(
            workspaceId=workspaceId, userId=senderId, permission=rcp_permission
        )
        if not checkSenderPermission and requestType == "invitation":
            raise Exception("You don't have permission to send request")

        newRequest = RequestService.insertNewRequest(
            requestType,
            content,
            createdAt,
            status,
            workspaceId,
            senderId,
            recipientId,
            handlerId,
            fr_permission,
            to_permission,
            rcp_permission,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(newRequest, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)


@bpsky.route("/api/v1/request/deletion", methods=["POST"])
def deleteRequest():
    try:
        body = load_request_body(request)
        workspaceId = body["workspaceId"]
        requestIdList = body["requestIdList"]
        deletedAt = datetime.now()
        deletedRequests = RequestService.deleteRequests(
            workspaceId, requestIdList, deletedAt
        )
        return bpsky.response_class(
            response=jsonpickle.encode(deletedRequests, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)


@bpsky.route("/api/v1/request/approve", methods=["POST"])
def approveRequest():
    try:
        body = load_request_body(request)
        handlerId = get_id_from_token(get_token(request))
        requestIdList = body["requestIdList"]
        workspaceId = body["workspaceId"]
        data = RequestService.approveRequest(workspaceId, requestIdList, handlerId)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)


@bpsky.route("/api/v1/request/decline", methods=["POST"])
def declineRequest():
    try:
        body = load_request_body(request)
        handlerId = get_id_from_token(get_token(request))
        requestIdList = body["requestIdList"]
        workspaceId = body["workspaceId"]
        data = RequestService.declineRequest(workspaceId, requestIdList, handlerId)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        raise Exception(e)
