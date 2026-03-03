from data.repositories.survey_features.question import Question
from services.survey_service.init_questions import Initialize
from services.utils import Permission_check


class Question_service:
    @classmethod
    def check_if_sample_questions_initialized(cls):
        return Question.check_if_sample_questions_initialized()

    @classmethod
    def initialize_sample_questions(cls):
        check_if_sample_questions_initialized = (
            Question_service.check_if_sample_questions_initialized()
        )
        if check_if_sample_questions_initialized:
            return {"message": "Sample questions are already initialized"}

        Initialize.initialize_questions()
        # Initialize.initialize_question_options()
        return "Initialize successfully"

    @classmethod
    def get_all_questions(cls, project_id, user_id):
        is_user_has_access = Permission_check.check_user_has_access_survey(
            project_id, user_id
        )
        if not is_user_has_access:
            raise Exception("User has no access to the survey")

        questions_by_system = Question.get_sample_questions()
        questions_by_user = Question.get_user_questions()
        print(questions_by_system, questions_by_user)
        return {
            "questionsBySystem": [
                {
                    "questionId": question.question_id,
                    "content": question.content,
                    "questionType": question.question_type,
                    "domain": question.domain,
                    "origin": question.origin,
                }
                for question in questions_by_system
            ],
            "questionsByUser": [
                {
                    "questionId": question.question_id,
                    "content": question.content,
                    "questionType": question.question_type,
                    "domain": question.domain,
                    "origin": question.origin,
                    "contributorId": question.contributor_id,
                }
                for question in questions_by_user
            ],
        }

    @classmethod
    def get_question_by_id(cls, question_id):
        return Question.get_question_by_id(question_id)

    @classmethod
    def update_usage_count(cls, question_id):
        return Question.update_usage_count(question_id)
