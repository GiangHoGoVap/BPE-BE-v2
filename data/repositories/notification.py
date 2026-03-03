from data.repositories.utils import *
import json
from bpsky import socketio


class Notification_Item_Return:
    @classmethod
    def NotificationReturnItem(cls, result):
        return Notification(
            id=result[0],
            userId=result[1],
            createdAt=result[2],
            content=result[3],
            isStarred=result[4],
            isRead=result[5],
            notificationType=result[6],
            status=result[7],
            workspaceId=result[8] if len(result) > 8 else None,
            permission=result[9] if len(result) > 9 else None,
        )

    @classmethod
    def NotificationReturnSocketItem(cls, result):
        return json.dumps(
            {
                "id": result[0],
                "userId": result[1],
                "createdAt": result[2],
                "content": result[3],
                "isStarred": result[4],
                "isRead": result[5],
                "notificationType": result[6],
                "status": result[7],
                "workspaceId": result[8] if len(result) > 8 else None,
                "permission": result[9] if len(result) > 9 else None,
            },
            default=str,
        )


class Notification_Get(Notification_Item_Return):
    @classmethod
    def getAllNotifications(
        cls, userId, page, limit, isStarred, keyword=None, notificationType=None
    ):
        query = f"""SELECT id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission
                    FROM public.notification
                    WHERE userId='{userId}' AND isDeleted=false
                """
        if notificationType:
            query += f" AND notificationType='{notificationType}'"
        if isStarred:
            query += f" AND isStarred={isStarred}"
        if keyword:
            query += f" AND LOWER(content) LIKE LOWER('%{keyword}%')"
        query += " ORDER BY createdAt DESC"

        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                total = len(results)
                if page and limit:
                    page = int(page)
                    limit = int(limit)
                    query += f""" LIMIT {limit} OFFSET {(page-1 if page-1 >= 0 else 0)*limit}"""

                cursor.execute(query)
                results = cursor.fetchall()
                return {
                    "total": total,
                    "limit": limit,
                    "data": [
                        Notification_Get.NotificationReturnItem(result)
                        for result in results
                    ],
                }
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getStarredNotifications(cls, userId: str):
        query = f"""SELECT id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission 
                    FROM public.notification
                    WHERE userId='{userId}' AND isDeleted=false AND isStarred=true
                    ORDER BY createdAt DESC;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [
                    Notification_Get.NotificationReturnItem(result)
                    for result in results
                ]
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Notification_Update(Notification_Item_Return):
    @classmethod
    def starNotification(cls, notificationId: str, isStarred: bool):
        query = f"""UPDATE public.notification
                    SET isStarred={isStarred}
                    WHERE id='{notificationId}' AND isDeleted=false
                    RETURNING id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return Notification_Update.NotificationReturnItem(result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def readNotification(cls, notificationId: str):
        query = f"""UPDATE public.notification
                    SET isRead=true
                    WHERE id='{notificationId}'
                    RETURNING id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return Notification_Update.NotificationReturnItem(result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def updateNotificationStatus(cls, notificationId, status):
        query = f"""UPDATE public.notification
                    SET status='{status}'
                    WHERE id='{notificationId}' AND isDeleted=false
                    RETURNING id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return Notification_Update.NotificationReturnItem(result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Notification_Delete(Notification_Item_Return):
    @classmethod
    def deleteNotification(cls, notificationIdList, deletedAt):
        for notificationId in notificationIdList:
            query = f"""UPDATE public.notification
                    SET isDeleted=true, deletedAt='{deletedAt}'
                    WHERE id='{notificationId}'
                    RETURNING id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission;
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    # result = cursor.fetchone()
            except Exception as e:
                connection.rollback()
                raise Exception(e)

        return "Delete notification successfully"


class Notification_Insert(Notification_Item_Return):
    @classmethod
    def insertNewNotification(
        cls,
        userId: str,
        content: str,
        createdAt: str,
        isDeleted: bool,
        isStarred: bool,
        isRead: bool,
        notificationType: str,
        status: str,
        workspaceId: str = None,
        permission: str = None,
    ):
        query = f"""INSERT INTO public.notification
                    (userId, createdAt, content, isDeleted, isStarred, isRead, notificationType, status, 
                    workspaceId, permission)
                    VALUES('{userId}', '{createdAt}', '{content}', {isDeleted}, {isStarred}, {isRead}, 
                    '{notificationType}', '{status}', '{workspaceId}', '{permission}')
                    RETURNING id, userId, createdAt, content, isStarred, isRead, notificationType, status, 
                    workspaceId, permission;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                if result:
                    # only emit to the user who is being notified
                    socketio.emit(
                        "insertNewNotification_" + str(userId),
                        Notification_Insert.NotificationReturnSocketItem(result),
                    )
                    return Notification_Insert.NotificationReturnItem(result)
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Notification(
    Notification_Get, Notification_Insert, Notification_Update, Notification_Delete
):
    id = ""
    userId = ""
    createdAt = datetime.now()
    content = ""
    isDeleted = False
    isStarred = False
    isRead = False
    notificationType = ""
    status = ""
    workspaceId = ""
    permission = ""

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)

    def __str__(self) -> str:
        return f"""Notification(
            id={self.id},
            userId={self.userId},
            createdAt={self.createdAt},
            content={self.content},
            isDeleted={self.isDeleted},
            isStarred={self.isStarred},
            isRead={self.isRead},
            notificationType={self.notificationType},
            status={self.status}
            workspaceId={self.workspaceId},
            permission={self.permission}
        )"""
