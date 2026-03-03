from data.repositories.process_portfolio_features.feasibility import Feasibility
from services.utils import Permission_check


class Feasibility_service:
    @classmethod
    def edit_feasibility_of_process_versions(
        cls, workspace_id, process_version_version, user_id, total_score
    ):
        # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
        #     workspace_id, user_id
        # )
        # if not workspace_owner:
        #     raise Exception("permission denied")
        process_version = cls.check_if_process_version_exists_in_feasibility(
            process_version_version
        )
        if process_version:
            process_version_feasibility = cls.update_feasibility_of_process_version(
                process_version_version, total_score
            )
        else:
            process_version_feasibility = cls.add_feasibility_of_process_version(
                process_version_version, total_score
            )
        return process_version_feasibility

    @classmethod
    def check_if_process_version_exists_in_feasibility(cls, process_version_version):
        feasibility = Feasibility.check_if_process_version_exists_in_feasibility(
            process_version_version
        )
        return feasibility

    @classmethod
    def update_feasibility_of_process_version(
        cls, process_version_version, total_score
    ):
        return Feasibility.update_feasibility_of_process_version(
            process_version_version, total_score
        )

    @classmethod
    def add_feasibility_of_process_version(cls, process_version_version, total_score):
        return Feasibility.add_feasibility_of_active_process_version(
            process_version_version, total_score
        )

    @classmethod
    def get_feasibility_of_process_version(cls, process_version_version):
        return Feasibility.get_feasibility_of_process_version(process_version_version)
