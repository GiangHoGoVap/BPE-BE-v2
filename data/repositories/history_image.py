from data.repositories.utils import *


class HistoryImage:
    # id = data.BigAutoField(primary_key=True)
    project_id = 0
    process_id = 0
    xml_file_link = ""
    save_at = datetime.now()
    image_link = ""

    @classmethod
    def insert(cls, project_id, process_id, xml_file_link, image_link):
        query = """INSERT INTO public.history_image
                    (xml_file_link, project_id, process_id, save_at, image_link)
                    VALUES(%s, %s, %s, NOW(), %s);
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
                        image_link,
                    ),
                )
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_all_image_by_bpmn_file(cls, project_id, process_id, xml_file_link):
        query = """SELECT image_link, save_at
                    FROM public.history_image
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
                return list_tuple_to_dict(["image_link", "save_at"], cursor.fetchall())
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def count_all_image_by_bpmn_file(cls, project_id, process_id, xml_file_link):
        query = """SELECT image_link, save_at
                    FROM public.history_image
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
                return len(cursor.fetchall())
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete(cls, project_id, process_id, xml_file_link, image_link):
        query = """DELETE FROM public.history_image
                    WHERE xml_file_link=%s AND project_id=%s AND image_link=%s AND process_id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        xml_file_link,
                        project_id,
                        image_link,
                        process_id,
                    ),
                )
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete_oldest(cls, project_id, process_id, xml_file_link):
        query = """DELETE FROM public.history_image
                    WHERE xml_file_link=%s AND project_id=%s AND process_id=%s
                        AND save_at=(SELECT MIN(save_at) FROM public.history_image WHERE xml_file_link=%s 
                        AND project_id=%s AND process_id=%s);
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
                        xml_file_link,
                        project_id,
                        process_id,
                    ),
                )
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def dif_last_saved(cls, project_id, process_id, xml_file_link):
        query = """SELECT MIN(save_at)
                    FROM public.history_image
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
                result = cursor.fetchone()
                if result is None or result[0] is None:
                    return True
                last_saved = result[0]
                return last_saved + timedelta(seconds=10) < datetime.now()
        except Exception as e:
            connection.rollback()
            raise Exception(e)
