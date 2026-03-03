from data.models.survey_feature_models.question_model import (
    Question_in_section_model,
    Question_model,
    Section_model,
)
from data.repositories.survey_features.question_option import Question_option
from database.db import DatabaseConnector
from services.survey_service.init_question_data import init_questions


class Question_in_section:
    @classmethod
    def create_question_in_section(
        cls, section_id, sample_question, current_order_in_section
    ):
        # this method is for creating sample questions in a section
        session = DatabaseConnector.get_session()
        try:
            question_in_section = Question_in_section_model(
                section_id=section_id,
                question_id=sample_question.id,
                content=sample_question.content,
                is_deleted=sample_question.is_deleted,
                is_required=True,
                order_in_section=init_questions[current_order_in_section][
                    "order_in_section"
                ],
                weight=init_questions[current_order_in_section]["weight"],
                question_type=init_questions[current_order_in_section]["question_type"],
            )
            session.add(question_in_section)
            session.commit()
            session.close()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_questions_in_section(cls, section_id):
        session = DatabaseConnector.get_session()
        try:
            questions_in_section = (
                session.query(Question_in_section_model)
                .filter(
                    Question_in_section_model.section_id == section_id,
                    Question_in_section_model.is_deleted == False,
                )
                .order_by(Question_in_section_model.order_in_section)
                .all()
            )
            session.commit()
            return questions_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_questions_in_survey(cls, sections_list_in_survey):
        try:
            questions_in_survey = []
            # get questions in each section, but with multiple choice and branching questions,
            # query question_option table to get options for each question
            # group them by section
            # get question_options for first two question
            question_options_list = []
            for section in sections_list_in_survey:
                questions_in_section = cls.get_questions_in_section(section["id"])
                # only get question options for multiple choice and branching questions
                for question in questions_in_section:
                    if question.question_type in ["multiple_choice", "branching"]:
                        question_options = (
                            Question_option.get_question_options_in_question_in_section(
                                question.id
                            )
                        )
                        question_options_list.append(question_options)
                print("question_options_list: ", question_options_list)
                print("section: ", section)
                questions_in_survey.append(
                    {
                        "sectionId": section["id"],
                        "sectionName": section["name"],
                        "orderInSurvey": section["order_in_survey"],
                        "questions": [
                            {
                                "questionOptions": (
                                    [
                                        {
                                            "id": question_option_item[0],
                                            "content": question_option_item[1],
                                            "orderInQuestion": question_option_item[2],
                                        }
                                        for question_option in question_options_list
                                        for question_option_item in question_option
                                        if question_option_item[3] == question.id
                                    ]
                                    if question.question_type
                                    in ["multiple_choice", "branching"]
                                    else []
                                ),
                                "id": question.id,
                                "content": question.content,
                                "isDeleted": question.is_deleted,
                                "isRequired": question.is_required,
                                "orderInSection": question.order_in_section,
                                "weight": question.weight,
                                "questionType": question.question_type,
                            }
                            for question in questions_in_section
                        ],
                    }
                )
            return questions_in_survey
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_question_detail_in_survey(cls, question_in_section_id):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            session.commit()
            if question_in_section:
                return {
                    "id": question_in_section.id,
                    "content": question_in_section.content,
                    "isDeleted": question_in_section.is_deleted,
                    "isRequired": question_in_section.is_required,
                    "orderInSection": question_in_section.order_in_section,
                    "weight": question_in_section.weight,
                    "questionType": question_in_section.question_type,
                    "sectionId": question_in_section.section_id,
                    "questionId": question_in_section.question_id,
                }
            else:
                return None
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_question_detail_in_survey(
        cls,
        question_in_section_id,
        is_required,
        weight,
        content,
    ):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            if is_required is not None:
                question_in_section.is_required = is_required
            if weight is not None:
                question_in_section.weight = weight
            if content is not None:
                question_in_section.content = content

            session.commit()
            return {
                "id": question_in_section.id,
                "content": question_in_section.content,
                "isDeleted": question_in_section.is_deleted,
                "isRequired": question_in_section.is_required,
                "orderInSection": question_in_section.order_in_section,
                "weight": question_in_section.weight,
                "questionType": question_in_section.question_type,
                "sectionId": question_in_section.section_id,
            }
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_question_in_section_by_id(cls, question_in_section_id):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            session.close()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_order_of_question_in_section(cls, question_id, new_order_in_section):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_id)
                .first()
            )
            question_in_section.order_in_section = new_order_in_section
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_question_in_section(cls, question_in_section_id):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            question_in_section.is_deleted = True
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def change_question_type(cls, question_in_section_id, new_question_type):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            question_in_section.question_type = new_question_type
            session.commit()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def add_new_question_to_section(
        cls,
        section_id,
        content,
        order_in_section,
        weight,
        is_required,
        question_type,
        question_id=None,
    ):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = Question_in_section_model(
                section_id=section_id,
                question_id=question_id,
                content=content,
                is_deleted=False,
                is_required=is_required,
                order_in_section=order_in_section,
                weight=weight,
                question_type=question_type,
            )
            session.add(question_in_section)
            session.commit()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_question_id_in_question_in_section(
        cls, question_in_section_id, question_id
    ):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(Question_in_section_model.id == question_in_section_id)
                .first()
            )
            question_in_section.question_id = question_id
            session.commit()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def check_if_question_exists(cls, section_id, question_id):
        session = DatabaseConnector.get_session()
        try:
            question_in_section = (
                session.query(Question_in_section_model)
                .filter(
                    Question_in_section_model.section_id == section_id,
                    Question_in_section_model.question_id == question_id,
                    Question_in_section_model.is_deleted == False,
                )
                .first()
            )
            session.commit()
            return question_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_questions_in_section(cls, section_id):
        session = DatabaseConnector.get_session()
        try:
            questions_in_section = (
                session.query(Question_in_section_model)
                .filter(
                    Question_in_section_model.section_id == section_id,
                    Question_in_section_model.is_deleted == False,
                )
                .all()
            )
            for question_in_section in questions_in_section:
                question_in_section.is_deleted = True
            session.commit()
            return questions_in_section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_list_of_questions_in_survey(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            questions_in_survey = (
                session.query(Question_in_section_model)
                .join(
                    Section_model,
                    Question_in_section_model.section_id == Section_model.id,
                )
                .filter(
                    Section_model.survey_id == survey_id,
                    Question_in_section_model.is_deleted == False,
                    Section_model.is_deleted == False,
                )
                .order_by(
                    Section_model.order_in_survey,
                    Question_in_section_model.order_in_section,
                )
                .all()
            )
            session.commit()
            return questions_in_survey
        except Exception as e:
            session.rollback()
            raise Exception(e)
