from data.repositories.utils import *


class JoinWorkspaceReturnType:
    @classmethod
    def getAllMembersReturnType(cls, total, limit, results):
        return {
            "total": total,
            "limit": limit,
            "data": [
                {
                    "name": result[0],
                    "email": result[1],
                    "avatar": result[2],
                    "memberId": result[3],
                    "workspaceId": result[4],
                    "joinedAt": result[5],
                    "permission": result[6],
                }
                for result in results
            ],
        }

    @classmethod
    def getMemberReturnType(cls, result):
        return {
            "memberId": result[0],
            "workspaceId": result[1],
            "joinedAt": result[2],
            "permission": result[3],
            "isDeleted": result[4],
        }

    @classmethod
    def updatePermissionReturnType(cls, results):
        return [
            {
                "name": result[0],
                "email": result[1],
                "avatar": result[2],
                "memberId": result[3],
                "workspaceId": result[4],
                "joinedAt": result[5],
                "permission": result[6],
            }
            for result in results
        ]

    @classmethod
    def insertNewMemberReturnType(cls, result):
        return {
            "name": result[0],
            "email": result[1],
            "avatar": result[2],
            "memberId": result[3],
            "workspaceId": result[4],
            "joinedAt": result[5],
            "permission": result[6],
        }


class RemoveOwnerFromMemberList:
    @classmethod
    def removeOwnerFromMemberList(cls, workspaceId: str, memberIdList):
        print("this is member id list", memberIdList)
        query = f"""SELECT ownerId FROM public.workspace
                    WHERE workspace.id='{workspaceId}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                ownerId = result[0]
                # print("this is owner id", ownerId)
                if str(ownerId) in memberIdList:
                    memberIdList.remove(str(ownerId))
                    # print("this is member id list after remove", memberIdList)
                return memberIdList
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Join_Workspace_Get(RemoveOwnerFromMemberList, JoinWorkspaceReturnType):
    @classmethod
    def getAllMembers(
        cls, workspaceId: str, page: int, limit: int, keyword=None, permission=None
    ):
        query = f"""SELECT u.name, u.email, u.avatar, jw.memberId, jw.workspaceId, jw.joinedAt, jw.permission
                    FROM public.join_workspace jw, public.bpe_user u
                    WHERE jw.workspaceId = {workspaceId} AND jw.isDeleted=false AND jw.isWorkspaceDeleted=false 
                    AND u.id = jw.memberId
                """

        if keyword:
            query += f""" AND LOWER(u.name) LIKE LOWER('%{keyword}%')"""
        if permission:
            query += f""" AND jw.permission='{permission}'"""

        query += f""" ORDER BY jw.joinedAt DESC"""

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
                return Join_Workspace_Get.getAllMembersReturnType(
                    total=total, limit=limit, results=results
                )

        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getMember(cls, workspaceId: str, memberId: str):
        # print("this is member id", memberId, workspaceId)
        query = f"""SELECT memberId, workspaceId, joinedAt, permission, isDeleted 
                    FROM public.join_workspace
                    WHERE join_workspace.workspaceId='{workspaceId}' AND join_workspace.memberId='{memberId}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    return Join_Workspace_Get.getMemberReturnType(result=result)
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getListMemberIdAndPermissionInWorkspace(cls, workspaceId) -> list:
        query = f"""SELECT memberId, permission FROM public.join_workspace
                    WHERE workspaceId='{workspaceId}' AND isDeleted=false AND isWorkspaceDeleted=false;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return results
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_permission_by_users_id_list(cls, user_ids, workspace_id):
        # memberId is currently int, need to convert to string
        user_ids = [str(user_id) for user_id in user_ids]

        query = f"""SELECT memberid, permission FROM public.join_workspace
                    WHERE workspaceId='{workspace_id}' AND memberId IN ({','.join(user_ids)});
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [
                    {"user_id": result[0], "permission": result[1]}
                    for result in results
                ]
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Join_Workspace_Update(RemoveOwnerFromMemberList, JoinWorkspaceReturnType):
    @classmethod
    def updatePermission(
        cls, workspaceId, newMemberIdList, currentPermission, newPermission
    ) -> list:
        print("this is current permission", currentPermission, newPermission)
        connection = DatabaseConnector.get_connection()
        try:
            for memberId in newMemberIdList:
                query = f"""SELECT permission FROM public.join_workspace
                        WHERE workspaceId='{workspaceId}' AND memberId = '{memberId}';
                    """
                connection = DatabaseConnector.get_connection()
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    print("this is result", result)
                    if currentPermission:
                        if result[0] != currentPermission:
                            raise Exception("Current permission does not match")
                    query = f"""UPDATE public.join_workspace
                            SET permission='{newPermission}'
                            WHERE workspaceId='{workspaceId}' AND memberId='{memberId}';
                        """
                    cursor.execute(query)
                    print("update permission")
                    connection.commit()

            # return list of members in tuple but do not have comma in the end that have been updated
            query = f"""SELECT u.name, u.email, u.avatar, jw.memberId, jw.workspaceId, jw.joinedAt, jw.permission
                        FROM public.join_workspace jw, public.bpe_user u
                        WHERE jw.workspaceId='{workspaceId}' AND jw.memberId IN ({','.join(newMemberIdList)}) 
                        AND u.id = jw.memberId;
                    """

            connection = DatabaseConnector.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                # return [
                #     {
                #         "name": result[0],
                #         "email": result[1],
                #         "avatar": result[2],
                #         "memberId": result[3],
                #         "workspaceId": result[4],
                #         "joinedAt": result[5],
                #         "permission": result[6],
                #     }
                #     for result in results
                # ]
                return Join_Workspace_Update.updatePermissionReturnType(results=results)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def undoDeleteMember(cls, workspaceId, memberIdList):
        for memberId in memberIdList:
            query = f"""UPDATE public.join_workspace
                    SET isDeleted=false, leftAt = null
                    WHERE workspaceId='{workspaceId}' AND memberId='{memberId}';
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    return "Undo delete member successfully"
            except Exception as e:
                connection.rollback()
                raise Exception(e)


class Join_Workspace_Delete:
    @classmethod
    def deleteMember(cls, workspaceId: str, newMemberList, leftAt):
        for memberId in newMemberList:
            query = f"""UPDATE public.join_workspace
                    SET isDeleted=true, leftAt = '{leftAt}'
                    WHERE workspaceId='{workspaceId}' AND memberId='{memberId}';
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

            except Exception as e:
                connection.rollback()
                raise Exception(e)
        return "Delete member successfully"


class Join_Workspace_Insert(RemoveOwnerFromMemberList, JoinWorkspaceReturnType):
    @classmethod
    def insertNewMember(
        cls,
        memberId: str,
        workspaceId: str,
        joinedAt: str,
        permission: str,
        isDeleted: bool,
    ):
        print("this is isDeleted in data", isDeleted)
        if isDeleted:
            query = f"""UPDATE public.join_workspace
                        SET isDeleted=false, joinedAt='{joinedAt}', permission='{permission}'
                        WHERE memberId='{memberId}' AND workspaceId='{workspaceId}'
                        RETURNING memberId, workspaceId, joinedAt, permission;
                    """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    # return the updated member
                    query = f"""SELECT u.name, u.email, u.avatar, jw.memberId, jw.workspaceId, jw.joinedAt, 
                                jw.permission
                                FROM public.join_workspace jw, public.bpe_user u
                                WHERE jw.memberId='{memberId}' AND jw.workspaceId='{workspaceId}' AND u.id = jw.memberId;
                        """
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return Join_Workspace_Insert.insertNewMemberReturnType(
                        result=result
                    )

            except Exception as e:
                connection.rollback()
                raise Exception(e)
        else:
            query = f"""INSERT INTO public.join_workspace
                    (memberId, workspaceId, joinedAt, permission, isDeleted, isWorkspaceDeleted)
                    VALUES('{memberId}', '{workspaceId}', '{joinedAt}', '{permission}', false, false)
                    RETURNING memberId, workspaceId, joinedAt, permission;
                """
            connection = DatabaseConnector.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    result = cursor.fetchone()
                    # return the inserted member including name, email, avatar, joinedAt, permission,
                    # memberId, workspaceId
                    if result:
                        query = f"""SELECT u.name, u.email, u.avatar, jw.memberId, jw.workspaceId, jw.joinedAt, 
                                    jw.permission
                                FROM public.join_workspace jw, public.bpe_user u
                                WHERE jw.memberId='{memberId}' AND jw.workspaceId='{workspaceId}' 
                                AND u.id = jw.memberId;
                            """
                        cursor.execute(query)
                        result = cursor.fetchone()
                        return Join_Workspace_Insert.insertNewMemberReturnType(
                            result=result
                        )
                    else:
                        return None

            except Exception as e:
                connection.rollback()
                raise Exception(e)


class Join_Workspace(
    Join_Workspace_Get,
    Join_Workspace_Insert,
    Join_Workspace_Update,
    Join_Workspace_Delete,
):
    memberId = ""
    workspaceId = ""
    joinedAt = datetime.now()
    leftAt = datetime.now()
    permission = ""
    isDeleted = False
    isWorkspaceDeleted = False

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)
        vars(self).update(kwargs)

    def __str__(self):
        return f"""Join_Workspace(
            memberId={self.memberId},
            workspaceId={self.workspaceId},
            joinedAt={self.joinedAt},
            permission={self.permission},
            isDeleted={self.isDeleted},
            isWorkspaceDeleted={self.isWorkspaceDeleted},
        )"""
