from data.models.workspace_model import Workspace_model
from data.repositories.utils import *
import json
from bpsky import socketio


class Workspace_Socket_IO:
    def __init__(self, type_noti, user_id):
        self.type_noti = type_noti
        self.user_id = user_id


class Workspace_Returning_Type:
    @classmethod
    def singleFieldReturn(cls, result):
        return result[0]

    @classmethod
    def multipleFieldReturn(cls, result):
        return Workspace(
            id=result[0],
            name=result[1],
            description=result[2],
            createdAt=result[3],
            ownerId=result[4],
            background=result[5],
            icon=result[6],
        )

    @classmethod
    def allWorkspacesByUserReturn(cls, result, total, limit):
        return {
            "total": total,
            "limit": limit,
            "data": list_tuple_to_dict(
                [
                    "id",
                    "name",
                    "description",
                    "openedAt",
                    "ownerId",
                    "background",
                    "icon",
                    "isPinned",
                    "ownerName",
                    "ownerAvatar",
                    "ownerEmail",
                    "permission",
                ],
                result,
            ),
        }


class Workspace_Get(Workspace_Returning_Type):
    @classmethod
    def checkIfWorkspaceExists(cls, name, userId):
        query = f"""SELECT id
                    FROM public.workspace
                    WHERE name='{name}' AND ownerId='{userId}' AND isDeleted=false;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    return Workspace_Get.singleFieldReturn(result)
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getWorkspaceName(cls, workspaceId):
        query = f"""SELECT name
                    FROM public.workspace
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    return Workspace_Get.singleFieldReturn(result)
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getWorkspace(cls, workspaceId: str):
        query = f"""SELECT ownerId
                    FROM public.workspace
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    return Workspace_Get.singleFieldReturn(result)
                else:
                    return None
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getAllWorkspacesByUser(
        cls,
        user_id,
        page,
        limit,
        openedAt=None,
        ownerId=None,
        keyword=None,
        pinned=None,
    ) -> dict:
        # return all workspaces that user joined or owned, sort by openedAt from latest to oldest
        # if keyword is not empty, search in name and description
        # if ownerId is not empty, search by ownerId
        # if openedAt == "newest", sort by openedAt from latest to oldest
        # if openedAt == "oldest", sort by openedAt from oldest to latest
        # if page and limit is not empty, return workspaces in page and limit
        # else return all workspaces
        query = f"""SELECT w.id, w.name, w.description, rw.openedAt, w.ownerId, w.background, w.icon, rw.isPinned, 
                    u.name as ownerName, u.avatar as ownerAvatar, u.email as ownerEmail, jw.permission as permission
                    FROM public.workspace w, public.recent_opened_workspace rw, public.bpe_user u, 
                    public.join_workspace jw
                    WHERE w.id=rw.workspaceId AND rw.userId='{user_id}' AND w.isDeleted=false AND rw.isHided=false 
                    AND u.id=w.ownerId AND jw.workspaceId = rw.workspaceId AND jw.memberId = '{user_id}'
                    AND rw.isUserDeletedFromWorkspace = false AND jw.isDeleted = false
                """
        if pinned == "true":
            query += f""" AND rw.isPinned=true"""
        if keyword:
            query += f""" AND (LOWER(w.name) LIKE LOWER('%{keyword}%') OR LOWER(u.name) LIKE LOWER('%{keyword}%'))"""
        if ownerId:
            query += f""" AND w.ownerId='{ownerId}'"""
        if openedAt == "newest" or openedAt is None:
            query += f""" ORDER BY rw.openedAt DESC"""
        elif openedAt == "oldest":
            query += f""" ORDER BY rw.openedAt ASC"""
        # run the query to get the total result first, then run the query to get the result in page and limit
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                print(result)
                total = len(result)
                if page and limit:
                    page = int(page)
                    limit = int(limit)
                    query += f""" LIMIT {limit} OFFSET {(page-1 if page-1 >= 0 else 0)*limit}"""
                cursor.execute(query)
                result = cursor.fetchall()
                return Workspace_Get.allWorkspacesByUserReturn(result, total, limit)
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getTotalWorkspacesByUser(cls, userId: str):
        query = f"""SELECT COUNT(*) as total
                    FROM public.workspace w, public.recent_opened_workspace rw
                    WHERE w.id=rw.workspaceId AND rw.userId='{userId}' AND w.isDeleted=false AND rw.isHided=false;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return {
                    "total": result[0],
                }
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getWorkspaceByOwnerIdAndIsPersonal(cls, ownerId: str, isPersonal: bool) -> list:
        query = f"""SELECT id, name, description, createdAt, ownerId, background, icon, isPersonal, isDeleted
                    FROM public.workspace
                    WHERE ownerId='{ownerId}' AND isPersonal={isPersonal};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "id",
                        "name",
                        "description",
                        "createdAt",
                        "ownerId",
                        "background",
                        "icon",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getDeletedWorkspace(cls):
        query = f"""SELECT id, name, description, createdAt, ownerId, background, icon, isPersonal, isDeleted
                    FROM public.workspace
                    WHERE isDeleted=true;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "id",
                        "name",
                        "description",
                        "createdAt",
                        "ownerId",
                        "background",
                        "icon",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getDeletedWorkspaceByOwner(cls, ownerId: str):
        query = f"""SELECT id, name, description, createdAt, ownerId, background, icon, isPersonal, isDeleted
                    FROM public.workspace
                    WHERE isDeleted=true AND ownerId='{ownerId}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "id",
                        "name",
                        "description",
                        "createdAt",
                        "ownerId",
                        "background",
                        "icon",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getPinnedWorkspace(cls, userId: str):
        print("this is pinned workspace query: ")
        # get pinned workspace by owner, which join with recent_opened_workspace
        query = f"""SELECT id, name, description, createdAt, ownerId, background, icon, isPinned
                    FROM public.workspace, public.recent_opened_workspace
                    WHERE workspace.id=recent_opened_workspace.workspaceId AND recent_opened_workspace.isPinned=true 
                    AND userId = '{userId}' AND isDeleted=false AND isHided=false;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "id",
                        "name",
                        "description",
                        "createdAt",
                        "ownerId",
                        "background",
                        "icon",
                        "isPinned",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    # search workspace by keyword, search in name and description
    def searchWorkspaceByKeyword(cls, keyword: str, userId: str):
        query = f"""SELECT w.id, w.name, w.description, w.createdAt, w.ownerId, w.background, w.icon, rw.isPinned
                    FROM public.workspace w, public.recent_opened_workspace rw, public.bpe_user u
                    WHERE (LOWER(w.name) LIKE LOWER('%{keyword}%') OR LOWER(u.name) LIKE LOWER('%{keyword}%'))
                    AND w.isDeleted=false AND rw.isHided=false 
                    AND w.id=rw.workspaceId 
                    AND rw.userId='{userId}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "id",
                        "name",
                        "description",
                        "createdAt",
                        "ownerId",
                        "background",
                        "icon",
                        "isPinned",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Workspace_Insert:
    @classmethod
    def insertNewWorkspace(
        cls,
        name: str,
        description: str,
        createdAt: datetime,
        ownerId: str,
        background: str,
        icon: str,
        isPersonal: bool,
        isDeleted: bool,
    ):
        query = f"""INSERT INTO public.workspace
                    (name, description, createdAt, ownerId, background, icon, isPersonal, isDeleted)
                    VALUES('{name}', '{description}', '{createdAt}', '{ownerId}', '{background}', '{icon}', 
                    '{isPersonal}', '{isDeleted}')
                    RETURNING id, name, description, createdAt, ownerId, background, icon, isPersonal, isDeleted;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                if result:
                    return Workspace(
                        id=result[0],
                        name=result[1],
                        description=result[2],
                        createdAt=result[3],
                        ownerId=result[4],
                        background=result[5],
                        icon=result[6],
                    )
                else:
                    return None

        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Workspace_Update:
    @classmethod
    def updateWorkspaceDescription(cls, workspaceId: str, description: str) -> str:
        query = f"""UPDATE public.workspace
                    SET description='{description}'
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return "Update description success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def updateWorkspaceName(cls, workspaceId: str, name: str) -> str:
        query = f"""UPDATE public.workspace
                    SET name='{name}'
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                # notification_payload = {"type": "workspace", "id": id}
                # cursor.execute(
                #     f"NOTIFY update_workspace_name, '{json.dumps(notification_payload)}'"
                # )
                connection.commit()
                # after update workspace name, notify to the client by socketio
                socketio.emit(
                    "workspace_changes" + str(id),
                    json.dumps(
                        {
                            "type": "workspace",
                            "id": id,
                        },
                        default=str,
                    ),
                )
                # notify when workspace name is changed

                return "Update name success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def updateWorkspaceBackground(cls, workspaceId: str, background: str) -> str:
        query = f"""UPDATE public.workspace
                    SET background='{background}'
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return "Update background success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def updateWorkspaceIcon(cls, workspaceId: str, icon: str) -> str:
        query = f"""UPDATE public.workspace
                    SET icon='{icon}'
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return "Update icon success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def updateWorkspaceOwnership(cls, workspaceId: str, newOwnerId: str):
        query = f"""UPDATE public.workspace
                    SET ownerId={newOwnerId}
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return "Update ownership success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Workspace_Delete:
    @classmethod
    def deleteWorkspace(cls, workspaceId: str, deletedAt: datetime) -> str:
        query = f"""UPDATE public.workspace
                    SET isDeleted=true , deletedAt='{deletedAt}'
                    WHERE id={workspaceId};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return "Delete Workspace Success"
        except Exception as e:
            connection.rollback()
            raise Exception(e)


class Workspace(Workspace_Get, Workspace_Insert, Workspace_Update, Workspace_Delete):
    id = 0
    name = ""
    description = ""
    createdAt = datetime.now()
    ownerId = ""
    background = ""
    icon = ""
    isPersonal = False
    isDeleted = False
    deletedAt = datetime.now()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)
        vars(self).update(kwargs)

    @classmethod
    def check_if_user_is_workspace_owner(cls, workspace_id, user_id):
        session = DatabaseConnector.get_session()
        try:
            workspace = (
                session.query(Workspace_model)
                .filter(
                    Workspace_model.id == int(workspace_id),
                    Workspace_model.isdeleted == False,
                )
                .first()
            )
            session.commit()
            if workspace is not None:
                return workspace.ownerid == user_id
            else:
                return "Workspace not found"
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def edit_workspace_measurements(
        cls,
        workspace_id,
        targeted_cycle_time=None,
        worst_cycle_time=None,
        targeted_cost=None,
        worst_cost=None,
        targeted_quality=None,
        worst_quality=None,
        targeted_flexibility=None,
        worst_flexibility=None,
    ):
        session = DatabaseConnector.get_session()
        try:
            workspace = (
                session.query(Workspace_model)
                .filter(
                    Workspace_model.id == int(workspace_id),
                    Workspace_model.isdeleted == False,
                )
                .first()
            )
            if workspace:
                if targeted_cycle_time is not None:
                    workspace.targeted_cycle_time = targeted_cycle_time
                if worst_cycle_time is not None:
                    workspace.worst_cycle_time = worst_cycle_time
                if targeted_cost is not None:
                    workspace.targeted_cost = targeted_cost
                if worst_cost is not None:
                    workspace.worst_cost = worst_cost
                if targeted_quality is not None:
                    workspace.targeted_quality = targeted_quality
                if worst_quality is not None:
                    workspace.worst_quality = worst_quality
                if targeted_flexibility is not None:
                    workspace.targeted_flexibility = targeted_flexibility
                if worst_flexibility is not None:
                    workspace.worst_flexibility = worst_flexibility
            session.commit()
            return workspace
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_workspace_measurements(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            workspace = (
                session.query(
                    Workspace_model.targeted_cycle_time,
                    Workspace_model.worst_cycle_time,
                    Workspace_model.targeted_cost,
                    Workspace_model.worst_cost,
                    Workspace_model.targeted_quality,
                    Workspace_model.worst_quality,
                    Workspace_model.targeted_flexibility,
                    Workspace_model.worst_flexibility,
                )
                .filter(
                    Workspace_model.id == int(workspace_id),
                    Workspace_model.isdeleted == False,
                )
                .first()
            )
            session.commit()
            if workspace:
                return workspace
            else:
                return None
        except Exception as e:
            session.rollback()
            raise Exception(e)
