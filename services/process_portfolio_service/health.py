from data.repositories.process_portfolio_features.health import Health
from services.file_service.evaluate_result import EvaluatedResultService
from services.survey_service.survey_result import Survey_result_service
from services.utils import Permission_check
from services.workspace_service.workspace import WorkspaceService


class Measurements:
    def __init__(self, targeted, worst, current, threshold):
        self.targeted = targeted
        self.worst = worst
        self.current = current
        self.threshold = threshold


class Health_service:
    EXTENDED_HEALTH_METRICS = (
        "cycle_time",
        "cost",
        "quality",
        "flexibility",
        "in_process",
        "out_process",
    )

    @classmethod
    def get_health_of_active_process_versions_in_workspace(cls, workspace_id, user_id):
        workspace_owner = Permission_check.check_if_user_is_workspace_owner(
            workspace_id, user_id
        )
        if not workspace_owner:
            raise Exception("permission denied")

    @classmethod
    def edit_health_of_process_version(
        cls,
        workspace_id,
        process_version_version,
        user_id,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
    ):
        # workspace_owner = Permission_check.check_if_user_is_workspace_owner(
        #     workspace_id, user_id
        # )
        # if not workspace_owner:
        #     raise Exception("permission denied")

        # check if process version exists in table Health
        process_version = cls.check_if_process_version_exists_in_health(
            process_version_version
        )
        if process_version:
            process_version_health = cls.update_health_of_process_version(
                process_version_version,
                current_cycle_time,
                current_cost,
                current_quality,
                current_flexibility,
            )
        else:
            process_version_health = cls.add_health_of_process_version(
                process_version_version,
                current_cycle_time,
                current_cost,
                current_quality,
                current_flexibility,
            )
        return process_version_health

    @classmethod
    def check_if_process_version_exists_in_health(cls, process_version_version):
        health = Health.check_if_process_version_exists_in_health(
            process_version_version
        )
        return health

    @classmethod
    def update_health_of_process_version(
        cls,
        process_version_version,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
    ):
        return Health.update_health_of_process_version(
            process_version_version,
            current_cycle_time,
            current_cost,
            current_quality,
            current_flexibility,
        )

    @classmethod
    def add_health_of_process_version(
        cls,
        process_version_version,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
    ):
        return Health.add_health_of_process_version(
            process_version_version,
            current_cycle_time,
            current_cost,
            current_quality,
            current_flexibility,
        )

    @classmethod
    def get_health_of_process_version(cls, process_version_version):
        health_stats = Health.get_health_of_process_version(process_version_version)
        return health_stats

    @classmethod
    def calculate_total_score(cls, workspace_id, user_id, process_version_version):
        # get evaluation result, which is threshold values for each health metric
        # get workspace measurements as target and worst values
        # get survey result as the external quality of the process
        # calculate score for each metric using pl method
        evaluation_result = cls.get_evaluation_result_of_process_version(
            process_version_version
        )
        workspace_measurements = cls.get_workspace_measurements(workspace_id, user_id)
        process_version_measurements = cls.get_health_of_process_version(
            process_version_version
        )
        if (
            evaluation_result is None
            or workspace_measurements is None
            or process_version_measurements is None
        ):
            cls.save_total_score(process_version_version, None)
            return

        check = cls.check_values(
            evaluation_result, workspace_measurements, process_version_measurements
        )
        if check is None:
            cls.save_total_score(process_version_version, None)
            return

        # check if current is in range target and worst
        cycle_time_values = Measurements(
            workspace_measurements["targetedCycleTime"],
            workspace_measurements["worstCycleTime"],
            process_version_measurements.current_cycle_time,
            evaluation_result["totalCycleTime"],
        )
        cost_values = Measurements(
            workspace_measurements["targetedCost"],
            workspace_measurements["worstCost"],
            process_version_measurements.current_cost,
            evaluation_result["totalCost"],
        )
        quality_values = Measurements(
            workspace_measurements["targetedQuality"],
            workspace_measurements["worstQuality"],
            process_version_measurements.current_quality,
            evaluation_result["totalQuality"],
        )
        flexibility_values = Measurements(
            workspace_measurements["targetedFlexibility"],
            workspace_measurements["worstFlexibility"],
            process_version_measurements.current_flexibility,
            evaluation_result["totalFlexibility"],
        )

        current_values_check = cls.check_current_values(
            cycle_time_values, cost_values, quality_values, flexibility_values
        )
        if current_values_check is not None:
            return current_values_check

        cycle_time_score = cls.pl_method(cycle_time_values, "cycle_time")
        cost_score = cls.pl_method(cost_values, "cost")
        quality_score = cls.pl_method(quality_values, "quality")
        flexibility_score = cls.pl_method(flexibility_values, "flexibility")

        in_process_score = cls.get_in_process_score(evaluation_result)
        out_process_score = cls.get_out_process_score(evaluation_result)

        if in_process_score is not None and out_process_score is not None:
            total_score = (
                cycle_time_score
                + cost_score
                + quality_score
                + flexibility_score
                + in_process_score
                + out_process_score
            ) / len(cls.EXTENDED_HEALTH_METRICS)
        else:
            total_score = (
                cycle_time_score + cost_score + quality_score + flexibility_score
            ) / 4

        # save in database
        cls.save_total_score(process_version_version, total_score)

    @classmethod
    def get_in_process_score(cls, evaluation_result):
        if not evaluation_result:
            return None
        return cls.normalize_score(evaluation_result.get("inProcess"))

    @classmethod
    def get_out_process_score(cls, evaluation_result):
        if not evaluation_result:
            return None
        out_process_breakdown = evaluation_result.get("outProcessBreakdown")
        if out_process_breakdown:
            weighted_score = cls.calculate_weighted_out_process_score(
                out_process_breakdown
            )
            if weighted_score is not None:
                return weighted_score
        return cls.normalize_score(evaluation_result.get("outProcess"))

    @classmethod
    def calculate_weighted_out_process_score(cls, out_process_breakdown):
        if out_process_breakdown is None:
            return None

        components = [
            (
                out_process_breakdown.get("csat"),
                out_process_breakdown.get("csatWeight"),
            ),
            (out_process_breakdown.get("ces"), out_process_breakdown.get("cesWeight")),
            (out_process_breakdown.get("nps"), out_process_breakdown.get("npsWeight")),
        ]

        weighted_total = 0
        total_weight = 0
        for score, weight in components:
            if score is None or weight is None:
                continue
            weighted_total += cls.normalize_score(score) * weight
            total_weight += weight

        if total_weight == 0:
            return None
        return cls.normalize_score(weighted_total / total_weight)

    @classmethod
    def normalize_score(cls, value):
        if value is None:
            return None
        normalized_value = float(value)
        if normalized_value < 0:
            return 0
        if normalized_value > 1:
            return 1
        return normalized_value

    @classmethod
    def pl_method(cls, measurement_values, measurement_type):
        if measurement_type == "cycle_time" or measurement_type == "cost":
            if measurement_values.current >= measurement_values.threshold:
                return -abs(
                    measurement_values.current - measurement_values.threshold
                ) / abs(measurement_values.threshold - measurement_values.worst)
            return abs(measurement_values.current - measurement_values.threshold) / abs(
                measurement_values.targeted - measurement_values.threshold
            )
        else:
            if measurement_values.current >= measurement_values.threshold:
                return abs(
                    measurement_values.current - measurement_values.threshold
                ) / abs(measurement_values.targeted - measurement_values.threshold)
            return -abs(
                measurement_values.current - measurement_values.threshold
            ) / abs(measurement_values.threshold - measurement_values.worst)

    @classmethod
    def get_evaluation_result_of_process_version(cls, process_version_version):
        evaluation_result = (
            EvaluatedResultService.get_evaluation_result_of_process_version(
                process_version_version
            )
        )
        return evaluation_result

    @classmethod
    def get_workspace_measurements(cls, workspace_id, user_id):
        return WorkspaceService.get_workspace_measurements(workspace_id, user_id)

    @classmethod
    def check_values(
        cls, evaluation_result, workspace_measurements, process_version_measurements
    ):
        if evaluation_result:
            if evaluation_result["totalCycleTime"] is None:
                return None
            if evaluation_result["totalCost"] is None:
                return None
            if evaluation_result["totalQuality"] is None:
                return None
            if evaluation_result["totalFlexibility"] is None:
                return None

        if workspace_measurements:
            if workspace_measurements["targetedCycleTime"] is None:
                return None
            if workspace_measurements["worstCycleTime"] is None:
                return None
            if workspace_measurements["targetedCost"] is None:
                return None
            if workspace_measurements["worstCost"] is None:
                return None
            if workspace_measurements["targetedQuality"] is None:
                return None
            if workspace_measurements["worstQuality"] is None:
                return None
            if workspace_measurements["targetedFlexibility"] is None:
                return None
            if workspace_measurements["worstFlexibility"] is None:
                return None

        if process_version_measurements:
            if process_version_measurements.current_cycle_time is None:
                return None
            if process_version_measurements.current_cost is None:
                return None
            if process_version_measurements.current_quality is None:
                return None
            if process_version_measurements.current_flexibility is None:
                return None
        return True

    @classmethod
    def save_total_score(cls, process_version_version, total_score):
        return Health.save_total_score(process_version_version, total_score)

    @classmethod
    def get_external_quality_of_process_version(cls, process_version_version):
        return Survey_result_service.get_survey_result(process_version_version)

    @classmethod
    def delete_health_values(cls, version):
        return Health.delete_health_values(version)

    @classmethod
    def check_current_values(
        cls, cycle_time_values, cost_values, quality_values, flexibility_values
    ):
        if (
            cycle_time_values.current < cycle_time_values.targeted
            or cycle_time_values.current > cycle_time_values.worst
        ):
            return {
                "message": "Cycle time is not in the range of targeted and worst values"
            }
        if (
            cost_values.current < cost_values.targeted
            or cost_values.current > cost_values.worst
        ):
            return {"message": "Cost is not in the range of targeted and worst values"}
        if (
            quality_values.current > quality_values.targeted
            or quality_values.current < quality_values.worst
        ):
            return {
                "message": "Quality is not in the range of targeted and worst values"
            }
        if (
            flexibility_values.current > flexibility_values.targeted
            or flexibility_values.current < flexibility_values.worst
        ):
            return {
                "message": "Flexibility is not in the range of targeted and worst values"
            }
        return None
