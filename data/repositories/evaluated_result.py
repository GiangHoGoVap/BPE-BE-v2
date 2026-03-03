import json

from data.models.evaluation_model import Evaluation_result_model
from data.repositories.utils import *


class EvaluatedResult:
    xml_file_link = ""
    project_id = 0
    process_id = 0
    name = ""
    result = ""
    description = ""
    create_at = datetime.now()

    @classmethod
    def insert(
        cls,
        xml_file_link,
        project_id,
        process_id,
        name,
        result,
        description,
        process_version_version,
    ):
        query = """INSERT INTO public.evaluated_result
                    (xml_file_link, project_id, process_id, "name", "result", description, create_at, process_version_version)
                    VALUES(%s, %s, %s, %s, %s::jsonb, %s, NOW(), %s);
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        xml_file_link,
                        project_id,
                        process_id,
                        name,
                        json.dumps(result),
                        description,
                        process_version_version,
                    ),
                )
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_result_by_bpmn_file(cls, xml_file_link, project_id, process_id):
        query = """SELECT "name", "result", description, create_at
                    FROM public.evaluated_result
                    WHERE xml_file_link=%s AND project_id=%s AND process_id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        xml_file_link,
                        project_id,
                        process_id,
                    ),
                )
                return list_tuple_to_dict(
                    ["name", "result", "description", "create_at"], cursor.fetchall()
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get(cls, xml_file_link, project_id, process_id, name):
        query = """SELECT "name", "result", description, create_at
                    FROM public.evaluated_result
                    WHERE xml_file_link=%s AND project_id=%s AND "name"=%s AND process_id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        xml_file_link,
                        project_id,
                        name,
                        process_id,
                    ),
                )
                list_result = list_tuple_to_dict(
                    ["name", "result", "description", "create_at"], cursor.fetchall()
                )
                if len(list_result) == 0:
                    return {}
                return list_result[0]
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete(cls, xml_file_link, project_id, process_id, name):
        query = """DELETE FROM public.evaluated_result
                    WHERE xml_file_link=%s AND project_id=%s AND "name"=%s AND process_id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        xml_file_link,
                        project_id,
                        name,
                        process_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise Exception("result doesn't exist")
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_evaluation_result_of_process_version(cls, process_version_version):
        # get the latest evaluated result of the process version
        session = DatabaseConnector.get_session()
        try:
            result = (
                session.query(Evaluation_result_model)
                .filter(
                    Evaluation_result_model.process_version_version
                    == process_version_version
                )
                .order_by(Evaluation_result_model.create_at.desc())
                .first()
            )
            return result
        except Exception as e:
            session.rollback()
            raise Exception(e)
