from data.repositories.notification import Notification
from services.workspace_service.join_workspace import JoinWorkspaceService


class NotificationService_Get:
    @classmethod
    def getAllNotifications(
        cls, userId, page, limit, isStarred, keyword=None, notificationType=None
    ):
        notifications = Notification.getAllNotifications(
            userId, page, limit, isStarred, keyword, notificationType
        )
        if notifications is None:
            return None
        return notifications


class NotificationService_Update:
    @classmethod
    def deleteNotification(cls, notificationIdList, deletedAt):
        return Notification.deleteNotification(notificationIdList, deletedAt)

    @classmethod
    def starNotification(cls, notificationId, isStarred):
        return Notification.starNotification(notificationId, isStarred)

    @classmethod
    def readNotification(cls, notificationId):
        return Notification.readNotification(notificationId)

    @classmethod
    def updateNotificationStatus(cls, notificationId, status):
        return Notification.updateNotificationStatus(notificationId, status)

    @classmethod
    def acceptNotification(
        cls, userId, workspaceId, joinedAt, permission, notificationId, status
    ):
        JoinWorkspaceService.insertNewMember(
            memberId=userId,
            workspaceId=workspaceId,
            joinedAt=joinedAt,
            permission=permission,
        )
        updatedNotification = Notification.updateNotificationStatus(
            notificationId, status
        )
        return updatedNotification

    @classmethod
    def declineNotification(cls, notificationId, status):
        updatedNotification = Notification.updateNotificationStatus(
            notificationId, status
        )
        return updatedNotification


class NotificationService_Insert:
    @classmethod
    def insertNewNotification(
        cls,
        userId,
        content,
        createdAt,
        isDeleted,
        isStarred,
        isRead,
        notificationType,
        status,
        workspaceId=None,
        permission=None,
    ):
        notification = Notification.insertNewNotification(
            userId,
            content,
            createdAt,
            isDeleted,
            isStarred,
            isRead,
            notificationType,
            status,
            workspaceId,
            permission,
        )
        if notification is None:
            return None
        return notification


class NotificationService(
    NotificationService_Get, NotificationService_Insert, NotificationService_Update
):
    pass
