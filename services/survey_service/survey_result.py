from collections import defaultdict

from data.repositories.survey_features.response import Response
from data.repositories.survey_features.survey import Survey
from data.repositories.survey_features.survey_result import Survey_result
from services.survey_service.answer import Answer_service
from services.survey_service.question_in_section import Question_in_section_service
from services.survey_service.question_option import Question_option_service


class Survey_result_service:
    @classmethod
    def calculate_scores(cls, survey_id, current_number_of_responses):
        # get all answers for response_id
        # get all questions for survey_id
        # calculate scores
        # update response with scores
        ces_score = cls.calculate_ces_score(survey_id, current_number_of_responses)
        nps_score = cls.calculate_nps_score(survey_id, current_number_of_responses)
        csat_score = cls.calculate_csat_score(survey_id, current_number_of_responses)
        # get weight of each score in survey
        # calculate final score
        # update survey with final score
        weights_of_scores = Survey_result.get_weights_of_scores(survey_id)
        ces_weight = weights_of_scores.ces_weight
        nps_weight = weights_of_scores.nps_weight
        csat_weight = weights_of_scores.csat_weight
        if ces_weight + nps_weight + csat_weight == 0:
            total_score = 0
        else:
            total_score = (
                ces_score["ces_score"] * ces_weight
                + nps_score["nps_score"] * nps_weight
                + csat_score["csat_score"] * csat_weight
            ) / (ces_weight + nps_weight + csat_weight)

        # update survey with final score
        survey_result = cls.check_if_survey_result_exists(survey_id)
        if not survey_result:
            cls.create_survey_result(survey_id)
        cls.update_scores(
            survey_id,
            ces_score["ces_score"],
            nps_score["nps_score"],
            csat_score["csat_score"],
            round(total_score, 3),
        )
        return {
            "number_of_responses": current_number_of_responses,
            "ces_score": ces_score,
            "ces_weight": ces_weight,
            "nps_score": nps_score,
            "nps_weight": nps_weight,
            "csat_score": csat_score,
            "csat_weight": csat_weight,
            "total_score": round(total_score, 3),
        }

    @classmethod
    def get_number_of_responses_for_each_question(cls, question_id):
        number_of_responses = Answer_service.get_number_of_responses_for_each_question(question_id)
        return number_of_responses

    @classmethod
    def calculate_ces_or_csat_score(
        cls, survey_id, current_number_of_responses, question_type
    ):
        # get all ces answers for survey_id
        # get weight of ces questions
        # calculate ces score with formula: sum of ces answer of each question * weight of each question / total
        # number of responses
        # update survey with ces score
        list_of_weight_and_answers_of_questions_in_survey = (
            cls.get_list_of_weight_and_answers_of_questions_in_survey(
                survey_id, question_type
            )
        )
        dict_number_of_answers_each_question = defaultdict(int)
        for item in list_of_weight_and_answers_of_questions_in_survey:
            dict_number_of_answers_each_question[item["question_id"]] += 1

        total_number_of_responses = current_number_of_responses  # get from response
        sum_of_weight = 0  # sum of weight of all questions
        result = 0
        dict_positive_answers_for_each_question = (
            {}
        )  # table of number of answers has value 5, 6, 7, key is question_id, value is number of answers
        dict_weight = (
            {}
        )  # table of weight of each question, key is question_id, value is weight

        for item in list_of_weight_and_answers_of_questions_in_survey:
            if item["value"] in ["5", "6", "7"]:
                # get number of answers has value 5, 6, 7
                dict_positive_answers_for_each_question[item["question_id"]] = (
                    dict_positive_answers_for_each_question.get(item["question_id"], 0)
                    + 1
                )
                dict_weight[item["question_id"]] = item["weight"]
        for index in dict_weight:
            sum_of_weight += dict_weight[index]
        for index in dict_positive_answers_for_each_question:
            # denominator = total_number_of_responses * sum_of_weight
            denominator = dict_number_of_answers_each_question[index] * sum_of_weight
            if denominator == 0:
                result += 0
            else:
                result += (
                    dict_positive_answers_for_each_question[index]
                    * dict_weight[index]
                    / denominator
                )
        num_of_positive_answers = sum(
            dict_positive_answers_for_each_question.values()
        )  # sum of positive answers
        # return round(result, 3)
        return {
            "ces_score" if question_type == "ces" else "csat_score": round(result, 3),
            "list_of_weight_and_answers_of_questions_in_survey": list_of_weight_and_answers_of_questions_in_survey,
            "total_number_of_responses": total_number_of_responses,
            "sum_of_weight": sum_of_weight,
            "dict_positive_answers_for_each_question": dict_positive_answers_for_each_question,
            "dict_weight": dict_weight,
            "num_of_positive_answers": num_of_positive_answers,
        }

    @classmethod
    def calculate_ces_score(cls, survey_id, current_number_of_responses):
        return cls.calculate_ces_or_csat_score(
            survey_id, current_number_of_responses, "ces"
        )

    @classmethod
    def calculate_nps_score(cls, survey_id, current_number_of_responses):
        list_of_weight_and_answers_of_questions_in_survey = (
            cls.get_list_of_weight_and_answers_of_questions_in_survey(survey_id, "nps")
        )
        total_number_of_responses = current_number_of_responses
        sum_of_weight = 0
        result = 0
        dict_weight = {}
        dict_promoters_for_each_question = (
            {}
        )  # table of number of answers has value 9, 10, key is question_id, value is number of answers
        dict_passives_for_each_question = (
            {}
        )  # table of number of answers has value 7, 8, key is question_id, value is number of answers
        dict_detractors_for_each_question = (
            {}
        )  # table of number of answers has value 0, 1, 2, 3, 4, 5, 6, key is question_id, value is number of answers
        for item in list_of_weight_and_answers_of_questions_in_survey:
            if item["value"] in ["9", "10"]:
                dict_promoters_for_each_question[item["question_id"]] = (
                    dict_promoters_for_each_question.get(item["question_id"], 0) + 1
                )
                dict_weight[item["question_id"]] = item["weight"]
            elif item["value"] in ["7", "8"]:
                dict_passives_for_each_question[item["question_id"]] = (
                    dict_passives_for_each_question.get(item["question_id"], 0) + 1
                )
                dict_weight[item["question_id"]] = item["weight"]
            elif item["value"] in ["0", "1", "2", "3", "4", "5", "6"]:
                dict_detractors_for_each_question[item["question_id"]] = (
                    dict_detractors_for_each_question.get(item["question_id"], 0) + 1
                )
                dict_weight[item["question_id"]] = item["weight"]
        for index in dict_weight:
            sum_of_weight += dict_weight[index]
        for index in dict_promoters_for_each_question:
            denominator = total_number_of_responses * sum_of_weight
            if denominator == 0:
                result += 0
            else:
                result += (
                    dict_promoters_for_each_question[index]
                    * dict_weight[index]
                    / denominator
                )
        for index in dict_detractors_for_each_question:
            denominator = total_number_of_responses * sum_of_weight
            if denominator == 0:
                result -= 0
            else:
                result -= (
                    dict_detractors_for_each_question[index]
                    * dict_weight[index]
                    / denominator
                )

        # normalize the nps score to range [0,1]
        if current_number_of_responses == 0:
            result = 0
        else:
            result = (result + 1) / 2
        num_of_promoters = sum(dict_promoters_for_each_question.values())
        num_of_detractors = sum(dict_detractors_for_each_question.values())
        return {
            "nps_score": round(result, 3),
            "list_of_weight_and_answers_of_questions_in_survey": list_of_weight_and_answers_of_questions_in_survey,
            "total_number_of_responses": total_number_of_responses,
            "sum_of_weight": sum_of_weight,
            "dict_promoters_for_each_question": dict_promoters_for_each_question,
            "dict_passives_for_each_question": dict_passives_for_each_question,
            "dict_detractors_for_each_question": dict_detractors_for_each_question,
            "dict_weight": dict_weight,
            "num_of_promoters": num_of_promoters,
            "num_of_detractors": num_of_detractors,
        }

    @classmethod
    def calculate_csat_score(cls, survey_id, current_number_of_responses):
        return cls.calculate_ces_or_csat_score(
            survey_id, current_number_of_responses, "csat"
        )

    @classmethod
    def get_list_of_weight_and_answers_of_questions_in_survey(
        cls, survey_id, question_type
    ):
        list_of_weight_and_answers_of_questions_in_survey = (
            Survey_result.get_list_of_weight_and_answers_of_questions_in_survey(
                survey_id, question_type
            )
        )
        return [
            {
                "question_id": item.id,
                "value": item.value,
                "weight": item.weight,
            }
            for item in list_of_weight_and_answers_of_questions_in_survey
        ]

    @classmethod
    def get_survey_result(cls, process_version_version):
        survey = Survey.check_if_survey_exists(process_version_version)
        if not survey:
            return None
        survey_id = survey.id
        # recalculating scores for survey
        current_number_of_responses = Response.get_number_of_responses(survey_id)
        scores = cls.calculate_scores(survey_id, current_number_of_responses)
        survey_result = Survey_result.get_survey_result(survey_id)
        number_of_responses = Response.get_number_of_responses(survey_id)
        if not survey_result:
            return None
        return {
            "numberOfResponses": number_of_responses,
            "ces": {
                "score": survey_result.ces_score,
                "weight": scores["ces_weight"],
                "numOfPositiveAnswers": scores["ces_score"]["num_of_positive_answers"],
            },
            "nps": {
                "score": survey_result.nps_score,
                "weight": scores["nps_weight"],
                "numOfPromoters": scores["nps_score"]["num_of_promoters"],
                "numOfDetractors": scores["nps_score"]["num_of_detractors"],
            },
            "csat": {
                "score": survey_result.csat_score,
                "weight": scores["csat_weight"],
                "numOfPositiveAnswers": scores["ces_score"]["num_of_positive_answers"],
            },
            "totalScore": survey_result.total_score,
        }

    @classmethod
    def update_scores(cls, survey_id, ces_score, nps_score, csat_score, total_score):
        return Survey_result.update_scores(
            survey_id, ces_score, nps_score, csat_score, total_score
        )

    @classmethod
    def create_survey_result(cls, survey_id):
        return Survey_result.create_survey_result(survey_id)

    @classmethod
    def check_if_survey_result_exists(cls, survey_id):
        return Survey_result.check_if_survey_result_exists(survey_id)

    @classmethod
    def get_answer_details_for_multiple_questions(cls, question_in_section_id):
        list_of_question_options = (
            Question_option_service.get_question_options_in_question_in_section(
                question_in_section_id
            )
        )
        list_of_answers = Answer_service.get_list_of_answers_for_question(
            question_in_section_id
        )
        # get number of each question options
        dict_number_of_each_answer = defaultdict(int)
        for question_option in list_of_question_options:
            dict_number_of_each_answer[question_option.content] = 0
        for answer in list_of_answers:
            dict_number_of_each_answer[answer.value] += 1
        # calculate percentage of each answer
        # return list of all answers
        return {
            "questionId": question_in_section_id,
            "answers": [
                {
                    "value": key,
                    "numberOfAnswers": dict_number_of_each_answer[key],
                    "percentage": round(
                        dict_number_of_each_answer[key] / len(list_of_answers) * 100, 2
                    )
                    if len(list_of_answers) > 0
                    else 0,
                }
                for key in dict_number_of_each_answer
            ],
        }

    @classmethod
    def get_answer_details(cls, process_version_version):
        # for each question, get all answers, count number of each answer, calculate percentage of each answer
        # with open questions, get all answers
        # return list of all answers`
        survey = Survey.check_if_survey_exists(process_version_version)
        if not survey:
            return None
        survey_id = survey.id
        list_of_questions = Question_in_section_service.get_list_of_questions_in_survey(
            survey_id
        )
        question_answers = []
        survey_result = cls.get_survey_result(process_version_version)
        for question in list_of_questions:
            question_type = question["questionType"]
            question_id = question["id"]

            if question_type in ["csat-in", "ces-in", "nps-in", "text"]:
                question_answers.append(
                    cls.get_answer_details_for_open_question(question_id)
                )
            elif question_type in ["csat", "ces"]:
                question_answers.append(
                    cls.get_answer_details_for_csat_or_ces_question(question_id)
                )
            elif question_type in ["nps"]:
                question_answers.append(
                    cls.get_answer_details_for_nps_question(question_id)
                )
            else:
                question_answers.append(
                    cls.get_answer_details_for_multiple_questions(question_id)
                )
        return {
            "surveyId": survey_id,
            "numberOfResponses": survey_result["numberOfResponses"]
            if survey_result
            else 0,
            "ces": {
                "score": survey_result["ces"]["score"] if survey_result else 0,
                "weight": survey_result["ces"]["weight"] if survey_result else 0,
                "numOfPositiveAnswers": survey_result["ces"]["numOfPositiveAnswers"]
                if survey_result
                else 0,
            },
            "nps": {
                "score": survey_result["nps"]["score"] if survey_result else 0,
                "weight": survey_result["nps"]["weight"] if survey_result else 0,
                "numOfPromoters": survey_result["nps"]["numOfPromoters"]
                if survey_result
                else 0,
                "numOfDetractors": survey_result["nps"]["numOfDetractors"]
                if survey_result
                else 0,
            },
            "csat": {
                "score": survey_result["csat"]["score"] if survey_result else 0,
                "weight": survey_result["csat"]["weight"] if survey_result else 0,
                "numOfPositiveAnswers": survey_result["csat"]["numOfPositiveAnswers"]
                if survey_result
                else 0,
            },
            "totalScore": survey_result["totalScore"] if survey_result else 0,
            "questions": [
                {
                    "totalResponses": sum(
                        [
                            answer["numberOfAnswers"]
                            if "numberOfAnswers" in answer
                            else 1
                            for answer in question_answers[index]["answers"]
                        ]
                    ),
                    "id": question["id"],
                    "content": question["content"],
                    "questionType": question["questionType"],
                    "questionResponses": question_answers[index]["answers"],
                }
                for index, question in enumerate(list_of_questions)
            ],
            # "answers": question_answers,
        }

    @classmethod
    def get_answer_details_for_csat_or_ces_question(cls, question_in_section_id):
        list_of_answers = Answer_service.get_list_of_answers_for_question(
            question_in_section_id
        )
        # get number of each answer
        dict_number_of_each_answer = {}
        for i in range(1, 8):
            dict_number_of_each_answer[i] = 0
        for answer in list_of_answers:
            dict_number_of_each_answer[int(answer.value)] += 1
        # calculate percentage of each answer
        # return list of all answers
        return {
            "question_id": question_in_section_id,
            "answers": [
                {
                    "value": key,
                    "numberOfAnswers": dict_number_of_each_answer[key],
                    "percentage": round(
                        dict_number_of_each_answer[key] / len(list_of_answers) * 100, 2
                    )
                    if len(list_of_answers) > 0
                    else 0,
                }
                for key in dict_number_of_each_answer
            ],
        }

    @classmethod
    def get_answer_details_for_nps_question(cls, question_id):
        list_of_answers = Answer_service.get_list_of_answers_for_question(question_id)
        # get number of each answer
        dict_number_of_each_answer = {}
        for i in range(0, 11):
            dict_number_of_each_answer[i] = 0

        for answer in list_of_answers:
            dict_number_of_each_answer[int(answer.value)] += 1

        # get number of each group: detractors, passives, promoters
        dict_number_of_each_group = {
            "detractors": 0,
            "passives": 0,
            "promoters": 0,
        }
        for i in range(0, 7):
            dict_number_of_each_group["detractors"] += dict_number_of_each_answer[i]
        for i in range(7, 9):
            dict_number_of_each_group["passives"] += dict_number_of_each_answer[i]
        for i in range(9, 11):
            dict_number_of_each_group["promoters"] += dict_number_of_each_answer[i]
        # calculate percentage of each answer
        # return list of all answers
        return {
            "questionId": question_id,
            "answers": [
                {
                    "value": key,
                    "numberOfAnswers": dict_number_of_each_answer[key],
                    "percentage": round(
                        dict_number_of_each_answer[key] / len(list_of_answers) * 100, 2
                    )
                    if len(list_of_answers) > 0
                    else 0,
                }
                for key in dict_number_of_each_answer
            ],
            "numberOfEachGroup": dict_number_of_each_group,
        }

    @classmethod
    def get_answer_details_for_open_question(cls, question_id):
        list_of_answers = Answer_service.get_list_of_answers_for_question(question_id)
        return {
            "questionId": question_id,
            "answers": [
                {
                    "id": answer.id,
                    "email": answer.email,
                    "fullName": answer.full_name,
                    "value": answer.value,
                }
                for answer in list_of_answers
            ],
        }
