from data.repositories.evaluated_result import EvaluatedResult
from services.project_service.work_on import WorkOnService
from services.survey_service.survey_result import Survey_result_service


class EvaluatedResultService:
    @classmethod
    def save(
        cls,
        user_id,
        xml_file_link,
        project_id,
        process_id,
        name,
        result,
        description,
        version,
    ):
        if not WorkOnService.can_edit(user_id, project_id):
            raise Exception("permission denied")
        EvaluatedResult.insert(
            xml_file_link, project_id, process_id, name, result, description, version
        )

    @classmethod
    def get_all_result_by_bpmn_file(
        cls, user_id, project_id, process_id, xml_file_link
    ):
        if not WorkOnService.can_view(user_id, project_id):
            raise Exception("permission denied")
        return EvaluatedResult.get_result_by_bpmn_file(
            xml_file_link, project_id, process_id
        )

    @classmethod
    def get_result(cls, user_id, project_id, process_id, xml_file_link, name):
        if not WorkOnService.can_view(user_id, project_id):
            raise Exception("permission denied")
        return EvaluatedResult.get(xml_file_link, project_id, process_id, name)

    @classmethod
    def delete(cls, user_id, xml_file_link, project_id, process_id, name):
        if not WorkOnService.can_edit(user_id, project_id):
            raise Exception("permission denied")
        EvaluatedResult.delete(xml_file_link, project_id, process_id, name)

    @classmethod
    def get_evaluation_result_of_process_version(cls, process_version_version):
        evaluation_result = EvaluatedResult.get_evaluation_result_of_process_version(
            process_version_version
        )

        # result is jsonb
        # extract total cycle time, total cost, total quality, total flexibility from result
        if evaluation_result is None:
            return None
        survey_result = Survey_result_service.get_survey_result(process_version_version)
        print("survey_result", survey_result)
        raw_result = evaluation_result.result
        if isinstance(raw_result, list):
            if len(raw_result) == 0:
                return None
            result = raw_result[0]
        elif isinstance(raw_result, dict):
            result = raw_result
        else:
            return None

        if not isinstance(result, dict):
            return None

        out_process_score = survey_result["totalScore"] if survey_result else None
        return {
            "totalCycleTime": result.get("totalCycleTime"),
            "totalCost": result.get("totalCost"),
            "totalQuality": (
                (result.get("quality") + out_process_score) / 2
                if out_process_score is not None and result.get("quality") is not None
                else None
            ),
            "totalFlexibility": result.get("flexibility"),
            "inProcess": result.get("quality"),
            "outProcess": out_process_score,
            "outProcessBreakdown": (
                {
                    "csat": survey_result["csat"]["score"],
                    "ces": survey_result["ces"]["score"],
                    "nps": survey_result["nps"]["score"],
                    "csatWeight": survey_result["csat"]["weight"],
                    "cesWeight": survey_result["ces"]["weight"],
                    "npsWeight": survey_result["nps"]["weight"],
                }
                if survey_result is not None
                else None
            ),
        }
