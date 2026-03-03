from data.repositories.recent_opened_workspaces import Recent_Opened_Workspaces
from datetime import datetime


class RecentOpenedWorkspaceService_Get:
    pass


class RecentOpenedWorkspaceService_Insert:
    @classmethod
    def insert(cls, workspaceId, memberId, joinedAt, isDeleted):
        recent_opened_workspace = Recent_Opened_Workspaces.insert(
            workspaceId, memberId, joinedAt, isDeleted
        )
        return recent_opened_workspace


class RecentOpenedWorkspaceService_Update:
    @classmethod
    def pinOpenedWorkspace(cls, userId: str, workspaceId: str):
        recent_opened_workspace = Recent_Opened_Workspaces.pinOpenedWorkspace(
            workspaceId, userId
        )
        return recent_opened_workspace

    @classmethod
    def openWorkspace(cls, userId: str, workspaceId: str, openedAt: datetime):
        recent_opened_workspace = Recent_Opened_Workspaces.openWorkspace(
            workspaceId, userId, openedAt
        )
        return recent_opened_workspace


class RecentOpenedWorkspaceService(
    RecentOpenedWorkspaceService_Get,
    RecentOpenedWorkspaceService_Insert,
    RecentOpenedWorkspaceService_Update,
):
    pass
