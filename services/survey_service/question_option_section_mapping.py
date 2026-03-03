from data.repositories.survey_features.question_option_section_mapping import (
    Question_option_section_mapping,
)


class Question_option_section_mapping_service:
    @classmethod
    def create_sample_question_option_section_mapping(
        cls, question_options, sections_list_in_survey
    ):
        # if question option is yes, then map to section 1
        # if question option is no, then map to section 2
        current_section_index = 0
        section_id = 0
        for question_option in question_options:
            if question_option.content == "Yes":
                current_section_index = 1
                section_id = sections_list_in_survey[1]["id"]

            elif question_option.content == "No":
                current_section_index = 2
                section_id = sections_list_in_survey[2]["id"]

            Question_option_section_mapping.create_sample_question_option_section_mapping(
                question_option, section_id
            )

    @classmethod
    def delete_question_option_section_mapping(cls, question_in_section_id):
        return Question_option_section_mapping.delete_question_option_section_mapping(
            question_in_section_id
        )
