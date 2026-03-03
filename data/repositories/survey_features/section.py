from data.models.survey_feature_models.question_model import Section_model
from database.db import DatabaseConnector


class Section:
    @classmethod
    def create_section(cls, survey_id, name, order_in_survey):
        session = DatabaseConnector.get_session()
        try:
            section = Section_model(
                name=f"Section {name}",
                survey_id=survey_id,
                is_deleted=False,
                order_in_survey=order_in_survey,
            )
            session.add(section)
            session.commit()
            session.close()
            return section
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def create_sample_sections(cls, survey_id):
        # create 3 default sections for the survey
        # the first one contain branch questions
        # the second one is section including questions for users within the system
        # the third one is section including questions for users outside the system
        # the final one is section including nps questions
        section_list = []
        session = DatabaseConnector.get_session()
        try:
            for i in range(0, 4):
                section = cls.create_section(survey_id, i, i)
                section_list.append(
                    {
                        "id": section.id,
                        "name": section.name,
                        "survey_id": section.survey_id,
                        "isDeleted": section.is_deleted,
                        "order_in_survey": section.order_in_survey,
                    }
                )
            session.close()
            return section_list
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_sections_in_survey(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            sections = (
                session.query(Section_model)
                .filter(
                    Section_model.survey_id == survey_id,
                    Section_model.is_deleted == False,
                )
                .all()
            )
            section_list = []
            for section in sections:
                section_list.append(
                    {
                        "id": section.id,
                        "name": section.name,
                        "order_in_survey": section.order_in_survey,
                    }
                )
            session.close()
            return section_list
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_sections(cls, survey_id):
        session = DatabaseConnector.get_session()
        try:
            sections = (
                session.query(Section_model)
                .filter(
                    Section_model.survey_id == survey_id,
                    Section_model.is_deleted == False,
                )
                .all()
            )
            for section in sections:
                section.is_deleted = True
            session.commit()
            return sections
        except Exception as e:
            session.rollback()
            raise Exception(e)
