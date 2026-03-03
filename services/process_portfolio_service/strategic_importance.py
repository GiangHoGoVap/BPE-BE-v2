from data.repositories.process_portfolio_features.strategic_importance import (
    Strategic_importance,
)
from services.utils import Permission_check


class Strategic_importance_service:
    @classmethod
    def edit_strategic_importance_of_process_version(
        cls, workspace_id, process_version_version, user_id, total_score
    ):
        workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            workspace_id, user_id
        )
        if not workspace_owner:
            raise Exception("permission denied")
        process_version = cls.check_if_process_version_exists_in_strategic_importance(
            process_version_version
        )
        process_version_strategic_importance = None
        if process_version:
            process_version_strategic_importance = (
                cls.update_strategic_importance_of_process_version(
                    process_version_version, total_score
                )
            )
        else:
            process_version_strategic_importance = (
                cls.add_strategic_importance_of_process_version(
                    process_version_version, total_score
                )
            )
        return process_version_strategic_importance

    @classmethod
    def check_if_process_version_exists_in_strategic_importance(
        cls, process_version_version
    ):
        strategic_importance = Strategic_importance.check_if_process_version_exists_in_strategic_importance(
            process_version_version
        )
        return strategic_importance

    @classmethod
    def add_strategic_importance_of_process_version(
        cls, process_version_version, total_score
    ):
        return Strategic_importance.add_strategic_importance_of_active_process_version(
            process_version_version, total_score
        )

    @classmethod
    def update_strategic_importance_of_process_version(
        cls, process_version_version, total_score
    ):
        return (
            Strategic_importance.update_strategic_importance_of_active_process_version(
                process_version_version, total_score
            )
        )

    @classmethod
    def get_strategic_importance_of_process_version(cls, process_version_version):
        return Strategic_importance.get_strategic_importance_of_process_version(
            process_version_version
        )
