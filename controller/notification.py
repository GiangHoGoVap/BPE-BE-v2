from bpsky import bpsky
from controller.utils import *
import jsonpickle


@bpsky.route("/api/v1/user/notification", methods=["GET"])
def getAllNotifications():
    try:
        userId = get_id_from_token(get_token(request))
        keyword = request.args.get("keyword", None)
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        isStarred = request.args.get("isStarred", False)
        notificationType = request.args.get("notificationType", None)
        data = NotificationService.getAllNotifications(
            userId, page, limit, isStarred, keyword, notificationType
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/user/notification", methods=["POST"])
def insertNewNotification():
    try:
        body = load_request_body(request)
        userId = body["userId"]
        content = body["content"]
        createdAt = datetime.now()
        isDeleted = False
        isStarred = False
        isRead = False
        notificationType = body["notificationType"]
        status = body["status"]
        workspaceId = body["workspaceId"]
        permission = body["permission"]
        senderId = get_id_from_token(get_token(request))

        checkSenderPermission = CheckPermission.checkMemberPermission(
            workspaceId=workspaceId, userId=senderId, permission=permission
        )

        if not checkSenderPermission:
            raise Exception("You don't have permission to send notification")

        data = NotificationService.insertNewNotification(
            userId=userId,
            content=content,
            createdAt=createdAt,
            isDeleted=isDeleted,
            isStarred=isStarred,
            isRead=isRead,
            notificationType=notificationType,
            status=status,
            workspaceId=workspaceId,
            permission=permission,
        )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/user/notification/deletion", methods=["POST"])
def deleteNotification():
    try:
        body = load_request_body(request)
        notificationIdList = body["notificationIdList"]
        deletedAt = datetime.now()
        data = NotificationService.deleteNotification(notificationIdList, deletedAt)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/user/notification/star", methods=["POST"])
def starNotification():
    try:
        body = load_request_body(request)
        notificationId = body["notificationId"]
        isStarred = body["isStarred"]
        data = NotificationService.starNotification(notificationId, isStarred)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/user/notification/read", methods=["POST"])
def readNotification():
    try:
        body = load_request_body(request)
        notificationId = body["notificationId"]
        data = NotificationService.readNotification(notificationId)
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)


@bpsky.route("/api/v1/user/notification/action", methods=["POST"])
def handleNotification():
    try:
        body = load_request_body(request)
        notificationId = body["notificationId"]
        status = body["status"]
        data = 0
        if status == "declined":
            data = NotificationService.declineNotification(notificationId, status)
        elif status == "accepted":
            workspaceId = body["workspaceId"]
            userId = body["userId"]
            joinedAt = datetime.now()
            permission = body["permission"]
            data = NotificationService.acceptNotification(
                userId, workspaceId, joinedAt, permission, notificationId, status
            )
        return bpsky.response_class(
            response=jsonpickle.encode(data, unpicklable=False),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return bpsky.response_class(response=e.__str__(), status=500)
