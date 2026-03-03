from data.repositories.work_on import WorkOn


class WorkOnService_Insert:
    @classmethod
    def insert(cls, user_id, project_id, role):
        # check if user already joined the project, if yes, change isDeleted to false
        # if not, insert new member
        isDeleted = WorkOn.checkIfMemberAlreadyJoined(user_id, project_id)
        if isDeleted:
            return WorkOn.undoDeleteMember(user_id, project_id)
        return WorkOn.insert(user_id, project_id, role)

    @classmethod
    def insert_many(cls, users, project_id):
        return WorkOn.insert_many(users, project_id)

    @classmethod
    def insert_many_by_update_new_role(cls, users, project_id):
        return WorkOn.insert_many_by_update_new_role(users, project_id)


class WorkOnService_Update:
    @classmethod
    def update_role(cls, user_id, project_id, role):
        return WorkOn.update_role(user_id, project_id, role)

    @classmethod
    def update_many_role(cls, users, project_id):
        return WorkOn.update_many_role(users, project_id)

    @classmethod
    def updateMemberPermission(cls, newMemberIdList, permission, workspaceId):
        return WorkOn.updateMemberPermission(newMemberIdList, permission, workspaceId)


class WorkOnService_Get:
    @classmethod
    def get_all_project_by_user_id(
        cls,
        user_id,
        page,
        limit,
        workspaceId,
        createdAt=None,
        ownerId=None,
        keyword=None,
    ):
        return WorkOn.get_all_project_by_user_id(
            user_id,
            page,
            limit,
            workspaceId,
            createdAt,
            ownerId,
            keyword,
        )

    @classmethod
    def get_all_owned_project_by_user_id(cls, user_id):
        return WorkOn.get_all_owned_project_by_user_id(user_id)

    @classmethod
    def get_all_shared_project_by_user_id(cls, user_id):
        return WorkOn.get_all_shared_project_by_user_id(user_id)

    @classmethod
    def get_all_user_by_project_id(cls, project_id):
        return WorkOn.get_all_user_by_project_id(project_id)

    @classmethod
    def is_not_exists(cls, user_ids, project_id):
        return WorkOn.is_not_exists(user_ids, project_id)

    @classmethod
    def is_exists(cls, user_ids, project_id):
        return WorkOn.is_exists(user_ids, project_id)

    @classmethod
    def is_project_owner(cls, user_id, project_id) -> bool:
        return WorkOn.is_project_owner(user_id, project_id)

    @classmethod
    def can_edit(cls, user_id, project_id):
        return WorkOn.can_edit(user_id, project_id)

    @classmethod
    def can_share(cls, user_id, project_id):
        return WorkOn.can_share(user_id, project_id)

    @classmethod
    def can_view(cls, user_id, project_id):
        return WorkOn.can_view(user_id, project_id)


class WorkOnService_Delete:
    @classmethod
    def delete_many(cls, user_ids, project_id):
        return WorkOn.delete_many(user_ids, project_id)

    @classmethod
    def deleteMember(cls, newMemberList, leftAt):
        return WorkOn.deleteMember(newMemberList, leftAt)

    @classmethod
    def delete_all(cls, project_id):
        return WorkOn.delete_all(project_id)


class WorkOnService(
    WorkOnService_Insert, WorkOnService_Get, WorkOnService_Update, WorkOnService_Delete
):
    pass
