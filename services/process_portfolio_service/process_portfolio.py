from data.repositories.process_portfolio_features.process_portfolio import (
    Process_portfolio,
)
from services.process_portfolio_service.feasibility import Feasibility_service
from services.process_portfolio_service.health import Health_service
from services.process_portfolio_service.strategic_importance import (
    Strategic_importance_service,
)
from services.utils import Permission_check


class Process_portfolio_service:
    @classmethod
    def create_process_portfolio(
        cls, workspace_id, user_id, active_process_version_list
    ):
        try:
            # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            #     workspace_id, user_id
            # )
            # if not workspace_owner:
            #     raise Exception("permission denied")

            # check if item in active_process_version_list exists in table Health, Strategic Importance, Feasibility
            # check if process portfolio exists in table Process_portfolio
            process_portfolio = cls.check_if_process_portfolio_exists(workspace_id)
            if process_portfolio:
                return {
                    "processPortfolio": {
                        "id": process_portfolio.id,
                        "createdAt": process_portfolio.created_at,
                        "isDeleted": process_portfolio.is_deleted,
                        "workspaceId": process_portfolio.workspace_id,
                    },
                    "processVersion": {},
                }
            process_portfolio = Process_portfolio.add_process_portfolio(workspace_id)
            return {
                "id": process_portfolio.id,
                "createdAt": process_portfolio.created_at,
                "isDeleted": process_portfolio.is_deleted,
                "workspaceId": process_portfolio.workspace_id,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def check_if_process_portfolio_exists(cls, workspace_id):
        return Process_portfolio.check_if_process_portfolio_exists(workspace_id)

    @classmethod
    def check_if_active_process_versions_have_health_strategic_importance_feasibility(
        cls, active_process_version_list
    ):
        try:
            for active_process_version in active_process_version_list:
                Health_service.check_if_process_version_exists_in_health(
                    active_process_version
                )
                Feasibility_service.check_if_process_version_exists_in_feasibility(
                    active_process_version
                )
                Strategic_importance_service.check_if_process_version_exists_in_strategic_importance(
                    active_process_version
                )
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_process_portfolio_content(cls, workspace_id, user_id):
        try:
            # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            #     workspace_id, user_id
            # )
            # if not workspace_owner:
            #     raise Exception("permission denied")
            # process_portfolio = cls.check_if_process_portfolio_exists(workspace_id)
            # if not process_portfolio:
            #     return None
            # return stats of every active process version in workspace
            eligible_process_versions_list = cls.get_eligible_process_versions(
                workspace_id
            )
            return {
                "processPortfolio": [
                    {
                        "processVersionVersion": process_version.version,
                        "health": process_version.health,
                        "strategicImportance": process_version.strategic_importance,
                        "feasibility": process_version.feasibility,
                        "projectName": process_version.project_name,
                        "processName": process_version.process_name,
                        "num": process_version.num,
                    }
                    for process_version in eligible_process_versions_list
                ]
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_process_version_stats(cls, workspace_id):
        try:
            process_version_stats = []
            active_process_versions = Process_portfolio.get_active_process_versions(
                workspace_id
            )
            for active_process_version in active_process_versions:
                process_version_stats.append(
                    {
                        "processVersionVersion": active_process_version.version,
                        "health": Health_service.get_health_of_process_version(
                            active_process_version.version
                        ),
                        "strategicImportance": Strategic_importance_service.get_strategic_importance_of_active_process_version(
                            active_process_version.version
                        ),
                        "feasibility": Feasibility_service.get_feasibility_of_active_process_version(
                            active_process_version.version
                        ),
                    }
                )
            return process_version_stats
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_measurements_of_process_version(
        cls, workspace_id, user_id, process_version_version
    ):
        # get current health, strategic importance, feasibility of
        try:
            # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            #     workspace_id, user_id
            # )
            # if not workspace_owner:
            #     raise Exception("permission denied")

            evaluation_result = cls.get_evaluation_result_of_process_version(
                process_version_version
            )
            health = Health_service.get_health_of_process_version(
                process_version_version
            )
            strategic_importance = Strategic_importance_service.get_strategic_importance_of_process_version(
                process_version_version
            )
            feasibility = Feasibility_service.get_feasibility_of_process_version(
                process_version_version
            )
            return {
                "health": {
                    "currentCycleTime": health.current_cycle_time,
                    "currentCost": health.current_cost,
                    "currentQuality": health.current_quality,
                    "currentFlexibility": health.current_flexibility,
                }
                if health
                else None,
                "strategicImportance": strategic_importance.total_score
                if strategic_importance
                else None,
                "feasibility": feasibility.total_score if feasibility else None,
                "evaluationResult": evaluation_result,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_evaluation_result_of_process_version(cls, process_version_version):
        return Health_service.get_evaluation_result_of_process_version(
            process_version_version
        )

    @classmethod
    def edit_measurements_of_process_version(
        cls,
        workspace_id,
        process_version_version,
        user_id,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
        strategic_importance,
        feasibility,
    ):
        try:
            # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            #     workspace_id, user_id
            # )
            # if not workspace_owner:
            #     raise Exception("permission denied")

            health = Health_service.edit_health_of_process_version(
                workspace_id,
                process_version_version,
                user_id,
                current_cycle_time,
                current_cost,
                current_quality,
                current_flexibility,
            )
            strategic_importance_score = Strategic_importance_service.edit_strategic_importance_of_process_version(
                workspace_id, process_version_version, user_id, strategic_importance
            )
            feasibility_score = (
                Feasibility_service.edit_feasibility_of_process_versions(
                    workspace_id, process_version_version, user_id, feasibility
                )
            )
            return {
                "health": {
                    "currentCycleTime": health.current_cycle_time,
                    "currentCost": health.current_cost,
                    "currentQuality": health.current_quality,
                    "currentFlexibility": health.current_flexibility,
                },
                "strategicImportance": strategic_importance_score.total_score,
                "feasibility": feasibility_score.total_score,
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_not_available_process_versions(cls, workspace_id, user_id, page, limit):
        try:
            # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            #     workspace_id, user_id
            # )
            # if not workspace_owner:
            #     raise Exception("permission denied")
            process_versions = Process_portfolio.get_not_available_process_versions(
                workspace_id, page, limit
            )
            total = Process_portfolio.get_number_of_not_available_process_versions(
                workspace_id
            )
            return {
                "total": total,
                "limit": int(limit),
                "data": [
                    {
                        "processVersionVersion": process_version.version,
                        "projectId": process_version.project_id,
                        "num": process_version.num,
                        "processId": process_version.process_id,
                        "processName": process_version.process_name,
                        "health": process_version.health,
                        "strategicImportance": process_version.strategic_importance,
                        "feasibility": process_version.feasibility,
                    }
                    for process_version in process_versions
                ],
            }
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_eligible_process_versions(cls, workspace_id):
        # get health, feasibility and strategic_importance of process_versions that total_score is not None
        return Process_portfolio.get_eligible_process_versions(workspace_id)
