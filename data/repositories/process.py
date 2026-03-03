from .utils import *


class Process:
    project_id = 0
    id = 0
    name = ""
    last_saved = datetime.now()

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)

    @classmethod
    def insert(self, project_id, name):
        query = f"""INSERT INTO public.process
                    (project_id, "name", last_saved)
                    VALUES('{project_id}', '{name}', NOW())
                    RETURNING id, project_id, "name", last_saved;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return Process(
                    id=result[0],
                    project_id=result[1],
                    name=result[2],
                    last_saved=result[3],
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def update_name(self, project_id, id, name):
        query = f"""UPDATE public.process
                    SET "name"='{name}'
                    WHERE project_id={project_id} AND id='{id}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete(cls, project_id, id):
        query = f"""DELETE FROM public.process
                    WHERE id={id} AND project_id={project_id};
                    """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_project(cls, project_id):
        query = f"""SELECT id, "name", last_saved
                    FROM public.process
                    WHERE project_id={project_id};
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(["id", "name", "last_saved"], result)
        except Exception as e:
            connection.rollback()
            raise Exception(e)
