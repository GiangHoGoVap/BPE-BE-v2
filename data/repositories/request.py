from data.repositories.utils import *
from bpsky import socketio
import json


class FindDuplicateRequest:
    @classmethod
    def findDuplicateRequest(
        cls, requestType, content, status, createdAt, workspaceId, senderId, recipientId
    ):
        # find duplicate request
        # if after sending request, user be kicked out of workspace, then the request is deleted, so it is not a
        # duplicate request
        # if createdAt is different, if the discrepancy is less than 1 day, then it is a duplicate request
        query = f"""SELECT r.createdAt, r.status, jw.isDeleted
                    FROM public.request r, public.join_workspace jw
                    WHERE r.type='{requestType}' AND r.content='{content}' AND r.status='{status}' 
                    AND r.workspaceId='{workspaceId}' AND r.senderId='{senderId}' AND r.recipientId='{recipientId}' 
                    AND r.isDeleted=false AND r.isWorkspaceDeleted=false AND jw.memberId='{senderId}'
                    AND r.workspaceId=jw.workspaceId
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    recentCreatedAt = result[0]
                    resultStatus = result[1]
                    isDeleted = result[2]
                    print(recentCreatedAt, resultStatus, isDeleted)
                    if (
                        (createdAt - recentCreatedAt).days < 1
                        and resultStatus == "pending"
                        and isDeleted is False
                    ):
                        return True
                    else:
                        return False
                else:
                    return False
        except Exception as e:
            raise Exception(e)


class Request_Get:
    @classmethod
    def getAllRequests(
        cls, workspaceId, page, limit, keyword=None, request_type=None, status=None
    ):
        query = f"""SELECT id, type, content, createdAt, status, workspaceId, senderId, handlerId, recipientId, 
        fr_permission, to_permission, rcp_permission
                    FROM public.request
                    WHERE workspaceId='{workspaceId}' AND isDeleted=false AND isWorkspaceDeleted=false
                """

        if keyword:
            query += f""" AND LOWER(content) LIKE LOWER('%{keyword}%')"""
        if request_type:
            query += f""" AND type='{request_type}'"""
        if status:
            query += f""" AND status='{status}'"""

        query += f""" ORDER BY createdAt DESC"""

        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                total = len(result)

                if page and limit:
                    page = int(page)
                    limit = int(limit)
                    query += f""" LIMIT {limit} OFFSET {(page-1 if page-1 >= 0 else 0)*limit}"""

                cursor.execute(query)
                result = cursor.fetchall()

                if result:
                    return {
                        "total": total,
                        "limit": limit,
                        "data": [
                            {
                                "id": item[0],
                                "type": item[1],
                                "content": item[2],
                                "createdAt": item[3],
                                "status": item[4],
                                "workspaceId": item[5],
                                "senderId": item[6],
                                "handlerId": item[7],
                                "recipientId": item[8],
                                "frPermission": item[9],
                                "toPermission": item[10],
                                "rcpPermission": item[11],
                            }
                            for item in result
                        ],
                    }
                else:
                    return []
        except Exception as e:
            raise Exception(e)


class Request_Insert(FindDuplicateRequest):
    @classmethod
    def insertNewRequest(
        cls,
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
    ):
        isDuplicate = Request_Insert.findDuplicateRequest(
            requestType, content, status, createdAt, workspaceId, senderId, recipientId
        )
        if isDuplicate:
            return "Duplicate request"
        print(
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
        query = f"""INSERT INTO public.request
                    (type, content, createdAt, status, isDeleted, isWorkspaceDeleted, workspaceId, senderId, 
                    recipientId, handlerId, fr_permission, to_permission, rcp_permission)
                    VALUES('{requestType}', '{content}', '{createdAt}', '{status}', false, false, '{workspaceId}', 
                    '{senderId}', '{recipientId}', '{handlerId}', '{fr_permission}', '{to_permission}', 
                    '{rcp_permission}')
                    RETURNING id, type, content, createdAt, status, workspaceId, senderId, recipientId, handlerId, 
                    fr_permission, to_permission, rcp_permission;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                print(result)
                if result:
                    # send result to socket, channel "insertNewRequest"
                    socketio.emit(
                        "insertNewRequest",
                        json.dumps(
                            {
                                "id": result[0],
                                "type": result[1],
                                "content": result[2],
                                "createdAt": result[3],
                                "status": result[4],
                                "workspaceId": result[5],
                                "senderId": result[6],
                                "handlerId": result[7],
                                "recipientId": result[8],
                                "frPermission": result[9],
                                "toPermission": result[10],
                                "rcpPermission": result[11],
                            },
                            default=str,
                        ),
                    )

                    return {
                        "id": result[0],
                        "type": result[1],
                        "content": result[2],
                        "createdAt": result[3],
                        "status": result[4],
                        "workspaceId": result[5],
                        "senderId": result[6],
                        "handlerId": result[7],
                        "recipientId": result[8],
                        "frPermission": result[9],
                        "toPermission": result[10],
                        "rcpPermission": result[11],
                    }
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Request_Update:
    @classmethod
    def approveRequest(cls, workspaceId, requestIdList, handlerId):
        result = []
        for requestId in requestIdList:
            query = f"""UPDATE public.request
                        SET status='approved', handlerId='{handlerId}'
                        WHERE id='{requestId}' AND workspaceId='{workspaceId}'
                        RETURNING id, type, content, createdAt, status, workspaceId, senderId, handlerId, 
                        recipientId, fr_permission, to_permission, rcp_permission;
                    """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)

                    data = cursor.fetchone()
                    # push data to result
                    result.append(
                        {
                            "id": data[0],
                            "type": data[1],
                            "content": data[2],
                            "createdAt": data[3],
                            "status": data[4],
                            "workspaceId": data[5],
                            "senderId": data[6],
                            "handlerId": data[7],
                            "recipientId": data[8],
                            "frPermission": data[9],
                            "toPermission": data[10],
                            "rcpPermission": data[11],
                        }
                    )

            except Exception as e:
                connection.rollback()
                raise Exception(e)
        return result

    @classmethod
    def declineRequest(cls, workspaceId, requestIdList, handlerId):
        result = []
        for requestId in requestIdList:
            query = f"""UPDATE public.request
                    SET status='declined', handlerId='{handlerId}'
                    WHERE id='{requestId}' AND workspaceId='{workspaceId}'
                    RETURNING id, type, content, createdAt, status, workspaceId, senderId, handlerId, 
                    recipientId, fr_permission, to_permission, rcp_permission;
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    # connection.commit()
                    # rename column, fr_permission -> frPermission, to_permission -> toPermission,
                    # rcp_permission -> rcpPermission
                    data = cursor.fetchone()
                    result.append(
                        {
                            "id": data[0],
                            "type": data[1],
                            "content": data[2],
                            "createdAt": data[3],
                            "status": data[4],
                            "workspaceId": data[5],
                            "senderId": data[6],
                            "handlerId": data[7],
                            "recipientId": data[8],
                            "frPermission": data[9],
                            "toPermission": data[10],
                            "rcpPermission": data[11],
                        }
                    )
            except Exception as e:
                connection.rollback()
                raise Exception(e)

        return result


class Request_Delete:
    @classmethod
    def deleteRequests(cls, workspaceId, requestIdList, deletedAt):
        for requestId in requestIdList:
            query = f"""UPDATE public.request
                    SET isDeleted=true, deletedAt='{deletedAt}'
                    WHERE id='{requestId}' AND workspaceId='{workspaceId}'
                    RETURNING id, type, content, createdAt, status, workspaceId, senderId, handlerId, 
                    recipientId, fr_permission, to_permission, rcp_permission;
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

            except Exception as e:
                connection.rollback()
                raise Exception(e)

        return "Delete requests successfully"

    @classmethod
    def deleteRequestsWhenDeletingUser(cls, workspaceId, newMemberList, deletedAt):
        for memberId in newMemberList:
            query = f"""UPDATE public.request
                    SET isDeleted=true, deletedAt='{deletedAt}'
                    WHERE workspaceId='{workspaceId}' AND senderId = '{memberId}'
                    RETURNING id, type, content, createdAt, status, workspaceId, senderId, handlerId, 
                    recipientId, fr_permission, to_permission, rcp_permission;
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

            except Exception as e:
                connection.rollback()
                raise Exception(e)

        return "Delete requests successfully"


class Request(Request_Update, Request_Delete, Request_Get, Request_Insert):
    id = ""
    type = ""
    content = ""
    createdAt = datetime.now()
    status = ""
    isDeleted = False
    isWorkspaceDeleted = False
    workspaceId = ""
    senderId = ""
    handlerId = ""
    recipientId = ""
    fr_permission = ""
    to_permission = ""
    rcp_permission = ""

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)
        vars(self).update(kwargs)

    def __str__(self) -> str:
        return f"""Request(
            id={self.id},
            type={self.type},
            content={self.content},
            createdAt={self.createdAt},
            status={self.status},
            isDeleted={self.isDeleted},
            isWorkspaceDeleted={self.isWorkspaceDeleted},
            workspaceId={self.workspaceId},
            senderId={self.senderId},
            handlerId={self.handlerId},
            recipientId={self.recipientId},
            frPermission={self.fr_permission},
            toPermission={self.to_permission},
            rcpPermission={self.rcp_permission},
        )"""
