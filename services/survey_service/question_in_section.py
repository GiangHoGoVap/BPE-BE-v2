from data.repositories.survey_features.question import Question
from data.repositories.survey_features.question_in_section import Question_in_section
from data.repositories.survey_features.question_option import Question_option
from services.survey_service.question_option import Question_option_service
from services.survey_service.question_option_section_mapping import (
    Question_option_section_mapping_service,
)
from services.utils import Permission_check


class Question_in_section_service:
    @classmethod
    def create_sample_questions(cls, sections_list_in_survey):
        # get list of prepared questions from Question table
        sample_questions_list = Question.get_sample_questions()
        # then add each question to the section, order of them in section, weight, etc.
        # for the first section, add 2 first questions
        # for the second section, add questions 3 - 10
        # for the third section, add questions 11 - 14
        # for the fourth section, add question 15
        print("sections_list_in_survey: ", sections_list_in_survey)
        print("sample_questions_list: ", sample_questions_list)
        for section in sections_list_in_survey:
            if section["name"] == "Section 0":
                for j in range(0, 1):
                    # add question to the section
                    question_in_section = (
                        Question_in_section.create_question_in_section(
                            section["id"], sample_questions_list[j], j
                        )
                    )
                    # add question options to the question
                    question_options = Question_option.create_sample_question_option(
                        question_in_section, j
                    )
                    # for this branching question, create a sample mapping of question options to the next sections
                    question_options_section_mapping = Question_option_section_mapping_service.create_sample_question_option_section_mapping(
                        question_options, sections_list_in_survey
                    )

            elif section["name"] == "Section 1":
                for j in range(1, 10):
                    # add question to the section
                    question_in_section = (
                        Question_in_section.create_question_in_section(
                            section["id"], sample_questions_list[j], j
                        )
                    )
                    if sample_questions_list[j][3] in [
                        "multiple_choice",
                        "branching",
                    ]:
                        # add question options to the question
                        Question_option.create_sample_question_option(
                            question_in_section, j
                        )

            elif section["name"] == "Section 2":
                for j in range(10, 14):
                    # add question to the section
                    Question_in_section.create_question_in_section(
                        section["id"], sample_questions_list[j], j
                    )

            elif section["name"] == "Section 3":
                Question_in_section.create_question_in_section(
                    section["id"], sample_questions_list[14], 14
                )
                # add question to the section

                # add order of them in section, weight, etc.
        # then return the list of questions in the survey
        return Question_in_section.get_questions_in_survey(sections_list_in_survey)

    @classmethod
    def get_questions_in_survey(cls, sections_list_in_survey):
        return Question_in_section.get_questions_in_survey(sections_list_in_survey)

    @classmethod
    def get_question_detail_in_survey(cls, question_in_section_id, project_id, user_id):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        question_in_section = Question_in_section.get_question_detail_in_survey(
            question_in_section_id
        )
        print("question_in_section: ", question_in_section)
        # if question_in_section.question_type in ["branching", "multiple_choice"]:
        question_options = Question_option.get_question_options_in_question_in_section(
            question_in_section_id
        )
        # return question_in_section and question_options, but question_options is a field of question_in_section
        return {
            "id": question_in_section["id"],
            "content": question_in_section["content"],
            "questionType": question_in_section["questionType"],
            "isRequired": question_in_section["isRequired"],
            "orderInSection": question_in_section["orderInSection"],
            "weight": question_in_section["weight"],
            "sectionId": question_in_section["sectionId"],
            "questionId": question_in_section["questionId"],
            "isDeleted": question_in_section["isDeleted"],
            "questionOptions": [
                {
                    "id": question_option[0],
                    "content": question_option[1],
                    "orderInQuestion": question_option[2],
                    "questionInSectionId": question_option[3],
                }
                for question_option in question_options
            ],
        }

    @classmethod
    def update_question_detail_in_survey(
        cls,
        user_id,
        project_id,
        section_id,
        question_in_section_id,
        question_type=None,
        is_required=None,
        order_in_section=None,
        weight=None,
        content=None,
        question_options=None,
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        if content == "":
            return {"message": "Question content cannot be empty"}

        if order_in_section is not None:  # means the question is being changed position
            # get number of questions in the section
            number_of_questions_in_section = len(
                Question_in_section.get_questions_in_section(section_id)
            )
            if order_in_section != 0 and (
                order_in_section > number_of_questions_in_section - 1
                or order_in_section < 0
            ):
                return {"message": "Invalid order in section"}
            cls.reorder_questions_in_section_when_change_position(
                section_id, question_in_section_id, order_in_section
            )
        if question_type:  # means the question type is being changed
            cls.change_question_type(question_in_section_id, question_type)

        if question_options:
            cls.handle_question_options(question_in_section_id, question_options)
        updated_question = Question_in_section.update_question_detail_in_survey(
            question_in_section_id,
            is_required,
            weight,
            content,
        )
        return cls.get_question_detail_in_survey(
            question_in_section_id, project_id, user_id
        )

    @classmethod
    def handle_question_options(cls, question_in_section_id, new_question_options):
        # check if the question_option is being deleted or added
        # if the question_option is deleted, then delete the question_option
        # if the question_option is added, then add the question_option
        # if the question_option is updated, then update the question_option
        current_question_options = (
            Question_option.get_question_options_in_question_in_section(
                question_in_section_id
            )
        )
        for current_question_option in current_question_options:
            # if the current question_option is not in the list passed in, then delete the question_option
            # the list passed in is the list of new question options, each question_option has an id
            if current_question_option[0] not in [
                new_question_option["id"]
                for new_question_option in new_question_options
            ]:
                print("current_question_option: ", current_question_option)
                Question_option_service.delete_question_option(current_question_option)

        for question_option in new_question_options:
            # if type id is int, then the question_option is being updated
            if isinstance(question_option["id"], int):
                Question_option_service.update_question_option(question_option)
            else:  # means the new question_option is being added
                Question_option_service.add_new_question_option(
                    question_in_section_id, question_option
                )
        # check if the question_option is being deleted
        # get the list of current question options of the question
        # if any question_option in the current list is not in the list passed in, then delete the question_option

    @classmethod
    def reorder_questions_in_section_when_delete_question(
        cls, section_id, question_in_section_id
    ):
        # question_in_section_id is the id of the question that is being changed position or deleted
        # when the question is being deleted, the order of the remaining questions in the section should be updated
        # when the question is being changed position, the order of the questions in the section should be updated

        # get the order of the question that is being changed position or deleted
        question_in_section = Question_in_section.get_question_in_section_by_id(
            question_in_section_id
        )
        order_of_question = question_in_section.order_in_section
        # get the list of questions in the section
        questions_in_section = Question_in_section.get_questions_in_section(section_id)
        # update the order of the questions in the section
        for question in questions_in_section:
            if (
                question.order_in_section > order_of_question
                and question.id != question_in_section_id
            ):
                Question_in_section.update_order_of_question_in_section(
                    question.id, question.order_in_section - 1
                )

        return {"message": "Questions in section have been reordered"}

    @classmethod
    def reorder_questions_in_section_when_change_position(
        cls, section_id, question_in_section_id, new_order
    ):
        # get the order of the question that is being changed position or deleted
        question_in_section = Question_in_section.get_question_in_section_by_id(
            question_in_section_id
        )
        order_of_question = question_in_section.order_in_section
        print("order_of_question: ", order_of_question)
        # get the list of questions in the section
        questions_in_section = Question_in_section.get_questions_in_section(section_id)
        # update the order of the questions in the section
        for question in questions_in_section:
            if order_of_question < question.order_in_section <= new_order:
                Question_in_section.update_order_of_question_in_section(
                    question.id, question.order_in_section - 1
                )
            elif order_of_question > question.order_in_section >= new_order:
                Question_in_section.update_order_of_question_in_section(
                    question.id, question.order_in_section + 1
                )

        # update the order of the question that is being changed position
        Question_in_section.update_order_of_question_in_section(
            question_in_section_id, new_order
        )
        return {"message": "Questions in section have been reordered"}

    @classmethod
    def delete_question_in_survey(
        cls, user_id, project_id, section_id, question_in_section_id
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        # delete the question in the section
        Question_in_section.delete_question_in_section(question_in_section_id)
        # delete the question options of the question if it has any
        Question_option.delete_question_options(question_in_section_id)
        # delete the question options section mapping of the question
        Question_option_section_mapping_service.delete_question_option_section_mapping(
            question_in_section_id
        )
        # reorder the questions in the section
        cls.reorder_questions_in_section_when_delete_question(
            section_id, question_in_section_id
        )
        return {"message": "Question has been deleted from the survey"}

    @classmethod
    def change_question_type(cls, question_in_section_id, new_question_type):
        # change question_type of the question
        # if the question is branching or multiple choice, then add question options to the question
        # if the question is already branching or multiple choice, then delete question options of the question
        # get the question in section
        question_in_section = Question_in_section.get_question_in_section_by_id(
            question_in_section_id
        )
        current_question_type = question_in_section.question_type
        # if the question is branching or multiple choice, then add question options to the question
        if new_question_type in ["branching", "multiple_choice"]:
            if current_question_type not in ["branching", "multiple_choice"]:
                question_options = Question_option.create_sample_question_option(
                    question_in_section, 1
                )
                # # for this branching question, create a sample mapping of question options to the next sections
                # question_options_section_mapping = Question_option_section_mapping_service.create_sample_question_option_section_mapping(
                #     question_options, Section_service.get_sections_in_survey()
                # )
        # if the question is already branching or multiple choice, then delete question options of the question
        else:
            if current_question_type in ["branching", "multiple_choice"]:
                Question_option.delete_question_options(question_in_section_id)
                # delete the question options section mapping of the question
                Question_option_section_mapping_service.delete_question_option_section_mapping(
                    question_in_section_id
                )
        return Question_in_section.change_question_type(
            question_in_section_id, new_question_type
        )

    @classmethod
    def add_new_question_to_section(
        cls,
        user_id,
        project_id,
        section_id,
        content,
        order_in_section,
        weight,
        is_required,
        question_type,
        question_options=None,
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        # add question to the section
        new_question_in_section = Question_in_section.add_new_question_to_section(
            section_id,
            content,
            order_in_section,
            weight,
            is_required,
            question_type,
        )
        # if the question_type is branching or multiple choice, then add question options to the question
        question_options_list = []
        if question_options:
            question_options_list = Question_option_service.create_question_options(
                new_question_in_section, question_options
            )
            # # for this branching question, create a sample mapping of question options to the next sections
            # question_options_section_mapping = Question_option_section_mapping_service.create_sample_question_option_section_mapping(
            #     question_options, Section_service.get_sections_in_survey()
            # )
        # when the question is added to the section, reorder the questions in the section
        cls.reorder_questions_in_section_when_add_new_question(
            section_id, new_question_in_section.id, order_in_section
        )
        return {
            "id": new_question_in_section.id,
            "content": new_question_in_section.content,
            "questionType": new_question_in_section.question_type,
            "isRequired": new_question_in_section.is_required,
            "orderInSection": new_question_in_section.order_in_section,
            "weight": new_question_in_section.weight,
            "sectionId": new_question_in_section.section_id,
            "questionOptions": [
                {
                    "id": question_option.id,
                    "content": question_option.content,
                    "orderInQuestion": question_option.order_in_question,
                    "questionInSectionId": question_option.question_in_section_id,
                }
                for question_option in question_options_list
            ],
        }

    @classmethod
    def contribute_question(
        cls,
        user_id,
        project_id,
        survey_domain,
        section_id,
        question_id,
        question_in_section_id,
        question_type,
        is_required,
        order_in_section,
        weight,
        content,
        question_options=None,
    ):
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        updated_question = cls.update_question_detail_in_survey(
            user_id,
            project_id,
            section_id,
            question_in_section_id,
            question_type,
            is_required,
            order_in_section,
            weight,
            content,
            question_options,
        )
        # check if the question exists
        question = Question.get_question_by_id(question_id)
        if question is not None:
            return Question.update_contributed_question(
                question_id, question_type, content, user_id
            )
        contributed_question = Question.contribute_question(
            question_type, content, user_id, survey_domain
        )
        # add the contributed question id to the question_in_section
        Question_in_section.update_question_id_in_question_in_section(
            question_in_section_id, contributed_question.id
        )
        return contributed_question

    @classmethod
    def reorder_questions_in_section_when_add_new_question(
        cls, section_id, new_question_in_section_id, order_in_section
    ):
        # get the list of questions in the section
        questions_in_section = Question_in_section.get_questions_in_section(section_id)
        # update the order of the questions in the section
        for question in questions_in_section:
            if (
                question.order_in_section >= order_in_section
                and question.id != new_question_in_section_id
            ):
                Question_in_section.update_order_of_question_in_section(
                    question.id, question.order_in_section + 1
                )
        # update the order of the new question in the section - already added
        # Question_in_section.update_order_of_question_in_section(
        #     new_question_in_section_id, order_in_section
        # )
        return {"message": "Questions in section have been reordered"}

    @classmethod
    def pick_question_from_suggestions(
        cls,
        user_id,
        project_id,
        section_id,
        question_id,
        order_in_section,
        user_action=None,
    ):
        # get question from table Question
        # check if the question is already in the section
        # if not, add the question to the section
        # if yes, return message "Question already in the section"
        # if the question is a multiple choice or branching, get the question options from table QuestionOption
        # if question is contributed by user, update the usage count
        # is_user_has_access = Permission_check.check_user_has_access_survey(
        #     project_id, user_id
        # )
        # if not is_user_has_access:
        #     raise Exception("User has no access to the survey")

        question = Question.get_question_by_id(question_id)

        existing_question_in_section = Question_in_section.check_if_question_exists(
            section_id, question_id
        )

        if existing_question_in_section and user_action is None:
            return {"message": "Question already in the section"}
        elif existing_question_in_section and user_action is not None:
            new_question_in_section = Question_in_section.add_new_question_to_section(
                section_id,
                question.content,
                order_in_section,
                1,
                False,
                question.question_type,
                question_id,
            )
            if question.question_type in ["branching", "multiple_choice"]:
                question_options = (
                    Question_option.get_question_options_with_question_id(
                        existing_question_in_section.id
                    )
                )
                for question_option in question_options:
                    Question_option_service.add_new_question_option(
                        new_question_in_section.id, question_option
                    )
        Question.update_usage_count(question_id)
        return {}

    @classmethod
    def get_questions_in_section(cls, section_id):
        return Question_in_section.get_questions_in_section(section_id)

    @classmethod
    def delete_questions_in_section(cls, section_id):
        deleted_questions = Question_in_section.delete_questions_in_section(section_id)
        return [
            {
                "id": question.id,
                "question_type": question.question_type,
            }
            for question in deleted_questions
        ]

    @classmethod
    def get_list_of_questions_in_survey(cls, survey_id):
        list_of_questions_in_survey = (
            Question_in_section.get_list_of_questions_in_survey(survey_id)
        )
        return [
            {
                "id": question.id,
                "content": question.content,
                "questionType": question.question_type,
                "isRequired": question.is_required,
                "orderInSection": question.order_in_section,
                "weight": question.weight,
                "sectionId": question.section_id,
            }
            for question in list_of_questions_in_survey
        ]
