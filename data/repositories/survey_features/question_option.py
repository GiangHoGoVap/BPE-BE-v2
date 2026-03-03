from data.models.survey_feature_models.question_model import Question_option_model
from database.db import DatabaseConnector
from services.survey_service.init_question_data import init_questions_options


class Question_option:
    @classmethod
    def create_sample_question_option(cls, question, current_question_index):
        # create question options for multiple choice questions and branching questions
        session = DatabaseConnector.get_session()
        question_options_list = []
        print("question: ", question)
        try:
            if current_question_index == 0:
                # this is branching questions
                # get first 2 options in init_questions_options and create them

                for i in range(0, 2):
                    question_option = Question_option_model(
                        question_in_section_id=question.id,
                        content=init_questions_options[i]["content"],
                        order_in_question=init_questions_options[i][
                            "order_in_question"
                        ],
                        is_deleted=question.is_deleted,
                    )
                    session.add(question_option)
                    session.commit()
                    question_options_list.append(question_option)

            elif current_question_index == 1:
                # this is multiple choice questions
                # get next 3 options in init_questions_options and create them
                for i in range(2, 5):
                    question_option = Question_option_model(
                        question_in_section_id=question.id,
                        content=init_questions_options[i]["content"],
                        order_in_question=init_questions_options[i][
                            "order_in_question"
                        ],
                        is_deleted=question.is_deleted,
                    )
                    session.add(question_option)
                    session.commit()
                    question_options_list.append(question_option)
            session.close()
            return question_options_list
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_question_options_in_question_in_section(
        cls, question_in_section_id: int
    ) -> list:
        session = DatabaseConnector.get_session()
        try:
            question_options = (
                session.query(
                    Question_option_model.id,
                    Question_option_model.content,
                    Question_option_model.order_in_question,
                    Question_option_model.question_in_section_id,
                )
                .filter(
                    Question_option_model.question_in_section_id
                    == question_in_section_id,
                    Question_option_model.is_deleted == False,
                )
                .order_by(Question_option_model.order_in_question)
                .all()
            )
            session.commit()
            return question_options
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_question_options(cls, question_in_section_id: int):
        session = DatabaseConnector.get_session()
        try:
            question_option = (
                session.query(Question_option_model)
                .filter(
                    Question_option_model.question_in_section_id
                    == question_in_section_id,
                    Question_option_model.is_deleted == False,
                )
                .all()
            )
            for option in question_option:
                option.is_deleted = True

            session.commit()
            return question_option
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def create_question_option(cls, question_in_section, question_option):
        session = DatabaseConnector.get_session()
        try:
            question_option = Question_option_model(
                question_in_section_id=question_in_section.id,
                content=question_option["content"],
                order_in_question=question_option["orderInQuestion"],
                is_deleted=question_in_section.is_deleted,
            )
            session.add(question_option)
            session.commit()
            return question_option
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_question_option(cls, question_option):
        session = DatabaseConnector.get_session()
        try:
            question_option = (
                session.query(Question_option_model)
                .filter(
                    Question_option_model.id == question_option["id"],
                    Question_option_model.is_deleted == False,
                )
                .update(
                    {
                        "content": question_option["content"],
                        "order_in_question": question_option["orderInQuestion"],
                    }
                )
            )
            session.commit()
            return question_option
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def add_new_question_option(
        cls, question_in_section_id: object, question_option: object
    ) -> object:
        session = DatabaseConnector.get_session()
        try:
            question_option = Question_option_model(
                question_in_section_id=question_in_section_id,
                content=question_option["content"],
                order_in_question=question_option["orderInQuestion"],
                is_deleted=False,
            )
            session.add(question_option)
            session.commit()
            return question_option
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_question_option(cls, question_option):
        session = DatabaseConnector.get_session()
        try:
            question_option = (
                session.query(Question_option_model)
                .filter(
                    Question_option_model.id == question_option[0],
                    Question_option_model.is_deleted == False,
                )
                .first()
            )
            question_option.is_deleted = True
            session.commit()
            return question_option
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_question_options_with_question_id(cls, question_in_section_id):
        session = DatabaseConnector.get_session()
        try:
            question_options = (
                session.query(Question_option_model)
                .filter(
                    Question_option_model.question_in_section_id
                    == question_in_section_id,
                    Question_option_model.is_deleted == False,
                )
                .all()
            )
            session.commit()
            return question_options
        except Exception as e:
            session.rollback()
            raise Exception(e)
