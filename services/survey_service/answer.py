from data.repositories.survey_features.answer import Answer


class Answer_service:
    @classmethod
    def add_answer(cls, response_id, question_id, value):
        return Answer.create_answer(response_id, question_id, value)

    @classmethod
    def get_all_answers(cls, response_id):
        return Answer.get_all_answers(response_id)

    @classmethod
    def delete_answers(cls, response_id):
        return Answer.delete_answers(response_id)

    @classmethod
    def get_list_of_answers_for_question(cls, question_id):
        list_of_answers = Answer.get_list_of_answers_for_question(question_id)
        return list_of_answers

    @classmethod
    def get_number_of_responses_for_each_question(cls, question_id):
        number_of_responses = Answer.get_number_of_responses_for_each_question(question_id)
