from data.repositories.survey_features.question_option import Question_option
from data.repositories.survey_features.question_option_section_mapping import (
    Question_option_section_mapping,
)


class Question_option_service:
    @classmethod
    def create_sample_question_option(cls, questions_list_in_survey):
        # only create question options for multiple choice questions and branching questions
        # they are the first 2 questions in the survey
        question_options = []
        for i in range(0, 2):
            question = questions_list_in_survey[i]
            if question["type"] in ["multiple_choice", "branching"]:
                # create question options
                question_options.append(
                    Question_option.create_sample_question_option(question, i)
                )
                # add question options to the question

        return question_options

    @classmethod
    def create_question_options(cls, question_in_section, question_options):
        # create question options for multiple choice questions and branching questions
        question_options_list = []
        for i in range(0, len(question_options)):
            question_option = Question_option.create_question_option(
                question_in_section, question_options[i]
            )
            question_options_list.append(question_option)
        return question_options_list

    @classmethod
    def update_question_option(cls, question_option):
        return Question_option.update_question_option(question_option)

    @classmethod
    def add_new_question_option(
        cls, question_in_section_id: int, question_option: object
    ) -> object:
        return Question_option.add_new_question_option(
            question_in_section_id, question_option
        )

    @classmethod
    def delete_question_option(cls, question_option):
        return Question_option.delete_question_option(question_option)

    @classmethod
    def delete_question_options(cls, question_in_section_id):
        return Question_option.delete_question_options(question_in_section_id)

    @classmethod
    def get_question_options_in_question_in_section(cls, question_in_section_id):
        return Question_option.get_question_options_in_question_in_section(
            question_in_section_id
        )
