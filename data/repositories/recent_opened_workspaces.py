from data.repositories.utils import *
import json


class Recent_Opened_Workspaces_Returning_Type:
    @classmethod
    def update_returning(cls, result):
        return Recent_Opened_Workspaces(
            workspaceId=result[0],
            userId=result[1],
            openedAt=result[2],
        )

    @classmethod
    def hide_workspace_message(cls, status):
        if status:
            return "Hided workspace successfully"
        else:
            return "Unhided workspace successfully"

    @classmethod
    def pin_workspace_message(cls, status):
        if status:
            return "Pinned workspace successfully"
        else:
            return "Unpinned workspace successfully"


class Recent_Opened_Workspaces_Get:
    pass


class Recent_Opened_Workspaces_Insert(Recent_Opened_Workspaces_Returning_Type):
    @classmethod
    def insert(cls, workspaceId, userId, openedAt, isDeleted):
        if isDeleted:
            query = f"""UPDATE public.recent_opened_workspace
                        SET isUserDeletedFromWorkspace=false, openedAt='{openedAt}'
                        WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                        RETURNING workspaceId, userId, openedAt;
                    """
        else:
            query = f"""INSERT INTO public.recent_opened_workspace(workspaceId, userId, openedAt, isHided, 
                        isPinned, isUserDeletedFromWorkspace)
                        VALUES('{workspaceId}', '{userId}', '{openedAt}', false, false, false)
                        RETURNING workspaceId, userId, openedAt;
                    """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return Recent_Opened_Workspaces_Insert.update_returning(result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Recent_Opened_Workspaces_Update(Recent_Opened_Workspaces_Returning_Type):
    @classmethod
    def hideOpenedWorkspace(cls, workspaceId, userId):
        query = f"""UPDATE public.recent_opened_workspace
                    SET isHided=true
                    WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                    RETURNING workspaceId, userId, openedAt;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                cursor.fetchone()
                return Recent_Opened_Workspaces_Update.hide_workspace_message(True)

        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def pinOpenedWorkspace(cls, workspaceId, userId):
        # query to find if workspace is pinned, if pinned then unpin it, if not pinned then pin it
        query = f"""SELECT isPinned FROM public.recent_opened_workspace
                    WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result[0]:
                    query = f"""UPDATE public.recent_opened_workspace
                                SET isPinned=false
                                WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                                RETURNING workspaceId, userId, openedAt;
                            """
                    status = False
                else:
                    query = f"""UPDATE public.recent_opened_workspace
                                SET isPinned=true
                                WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                                RETURNING workspaceId, userId, openedAt;
                            """
                    status = True
                cursor.execute(query)
                connection.commit()
                cursor.fetchone()
                return Recent_Opened_Workspaces_Update.pin_workspace_message(status)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def openWorkspace(cls, workspaceId, userId, openedAt):
        query = f"""SELECT * FROM public.recent_opened_workspace
                    WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result is None:
                    return Recent_Opened_Workspaces.insert(
                        workspaceId, userId, openedAt, False
                    )
                else:
                    query = f"""UPDATE public.recent_opened_workspace
                                SET openedAt='{openedAt}'
                                WHERE workspaceId='{workspaceId}' AND userId='{userId}'
                                RETURNING workspaceId, userId, openedAt;
                            """
                    cursor.execute(query)
                    connection.commit()
                    result = cursor.fetchone()
                    return Recent_Opened_Workspaces_Update.update_returning(result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Recent_Opened_Workspaces(
    Recent_Opened_Workspaces_Get,
    Recent_Opened_Workspaces_Insert,
    Recent_Opened_Workspaces_Update,
):
    workspaceId = ""
    userId = ""
    openedAt = ""
    isHided = False
    isPinned = False
    isWorkspaceDeleted = False

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)
