from data.repositories.join_workspace import Join_Workspace
from data.repositories.request import Request
from services.project_service.work_on import WorkOnService
from services.utils import PermissionConverter
from services.workspace_service.recent_opened_workspace import (
    RecentOpenedWorkspaceService,
)


class CheckPermission:
    @classmethod
    def checkMemberPermission(cls, workspaceId, userId, permission):
        sender = JoinWorkspaceService.getMember(workspaceId, userId)
        print("sender", sender)
        if sender is None:
            return False
        senderPermission = sender["permission"]
        if senderPermission == "viewer":
            if permission != "viewer":
                return False

        elif senderPermission == "sharer":
            if permission != "viewer" and permission != "sharer":
                return False
        return True


class JoinWorkspaceService_Get:
    @classmethod
    def getAllMembers(
        cls, workspaceId: str, page: int, limit: int, keyword=None, permission=None
    ):
        members = Join_Workspace.getAllMembers(
            workspaceId, page, limit, keyword, permission
        )
        if members is None:
            return None
        return members

    @classmethod
    def getMember(cls, workspaceId: str, memberId: str):
        member = Join_Workspace.getMember(workspaceId, memberId)
        if member is None:
            return None
        return member

    @classmethod
    def getListMemberIdAndPermissionInWorkspace(cls, workspaceId: str) -> list:
        return Join_Workspace.getListMemberIdAndPermissionInWorkspace(workspaceId)

    @classmethod
    def get_permission_by_users_id_list(cls, user_ids, workspace_id):
        return Join_Workspace.get_permission_by_users_id_list(user_ids, workspace_id)


class JoinWorkspaceService_Update:
    @classmethod
    def deleteMember(cls, workspaceId: str, memberIdList, leftAt):
        try:
            newMemberList = Join_Workspace.removeOwnerFromMemberList(
                workspaceId, memberIdList
            )
            if len(newMemberList) == 0:
                return None
            deleteJoinWorkspace = Join_Workspace.deleteMember(
                workspaceId, newMemberList, leftAt
            )
            # when member left workspace, delete all work on project of that member
            # and delete all requests of that member

            delete_work_on_status = WorkOnService.deleteMember(newMemberList, leftAt)
            print("delete_work_on_status", delete_work_on_status)
            Request.deleteRequestsWhenDeletingUser(workspaceId, newMemberList, leftAt)
            return deleteJoinWorkspace
        except Exception as e:
            raise Exception(e)

    @classmethod
    def updateMemberPermission(cls, workspaceId: str, memberIdList, permission: str):
        newMemberIdList = Join_Workspace.removeOwnerFromMemberList(
            workspaceId, memberIdList
        )
        if len(newMemberIdList) == 0:
            return None
        Join_Workspace.updatePermission(workspaceId, newMemberIdList, None, permission)
        # when member permission is updated, update all work on project of that member
        WorkOnService.updateMemberPermission(
            newMemberIdList,
            permission=PermissionConverter.convert_permission_to_role(permission),
            workspaceId=workspaceId,
        )
        return Join_Workspace.updatePermission(
            workspaceId, newMemberIdList, None, permission
        )

    @classmethod
    def undoDeleteMember(cls, workspaceId, memberIdList):
        return Join_Workspace.undoDeleteMember(workspaceId, memberIdList)


class JoinWorkspaceService_Insert:
    @classmethod
    def insertNewMember(
        cls,
        memberId: str,
        workspaceId: str,
        joinedAt: str,
        permission: str,
    ):
        # check if member already joined
        member = Join_Workspace.getMember(workspaceId=workspaceId, memberId=memberId)
        print("member", member)
        isDeleted = False
        if member is not None:
            isDeleted = member["isDeleted"]
            if not isDeleted:
                return None
        if member is None or isDeleted:
            newMember = Join_Workspace.insertNewMember(
                memberId, workspaceId, joinedAt, permission, isDeleted=isDeleted
            )
            RecentOpenedWorkspaceService.insert(
                workspaceId, memberId, joinedAt, isDeleted=isDeleted
            )
            # get list all projects in workspace
            from services.project_service.project import ProjectService

            list_project = ProjectService.getAllProjectsInWorkspace(workspaceId)
            print("list_project", list_project)
            # when new member join workspace, insert all work on project of that member
            for project in list_project:
                WorkOnService.insert(
                    memberId,
                    project[0],
                    PermissionConverter.convert_permission_to_role(permission),
                )
            return newMember
        return None


class JoinWorkspaceService(
    JoinWorkspaceService_Get, JoinWorkspaceService_Insert, JoinWorkspaceService_Update
):
    pass
