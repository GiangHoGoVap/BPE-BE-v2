from data.repositories.workspace import Workspace
from data.repositories.user import User


class NotificationContent:
    @classmethod
    def generateContent(
        cls,
        requestType,
        newPermission=None,
        fr_permission=None,
        to_permission=None,
        workspaceId=None,
        senderId=None,
    ):
        if requestType == "invitation":
            if workspaceId is None or senderId is None or newPermission is None:
                raise Exception("Missing workspaceId or senderId or newPermission")
            else:
                # get workspace name
                workspaceName = Workspace.getWorkspaceName(workspaceId)
                # get sender name
                senderName = User.getUserName(senderId)
                return f"{senderName} has invited you to join {workspaceName} with permission {newPermission}"

        elif requestType == "adjust permission":
            if (
                workspaceId is None
                or senderId is None
                or fr_permission is None
                or to_permission is None
            ):
                raise Exception(
                    "Missing workspaceId or senderId or fr_permission or to_permission"
                )
            else:
                # get workspace name
                workspaceName = Workspace.getWorkspaceName(workspaceId)
                # get sender name
                senderName = User.getUserName(senderId)
                return f"Your request to adjust your permission in {workspaceName} from {fr_permission} to {to_permission} has been approved"
