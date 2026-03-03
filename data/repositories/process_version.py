from data.models.process_model import Process_version_model, Process_model
from data.models.process_portfolio_feature_models.process_portfolio_model import (
    Feasibility_model,
    Strategic_importance_model,
    Health_model,
)
from data.models.project_model import Project_model
from data.repositories.utils import *


class ProcessVersion:
    xml_file_link = ""
    project_id = 0
    process_id = 0
    version = ""
    num = 0
    last_saved = datetime.now()

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)

    @classmethod
    def create_default(cls, xml_file_link, project_id, process_id, version):
        query = f"""INSERT INTO public.process_version
                            (xml_file_link, project_id, process_id, "version", num, last_saved, is_active)
                            VALUES('{xml_file_link}', {project_id}, {process_id}, '{version}',
                                CAST((SELECT CASE WHEN MAX(num) IS NULL THEN 0 ELSE MAX(num) END
                                    FROM public.process_version
                                    WHERE project_id={project_id} AND process_id={process_id})
                                    AS INT)+1,
                            NOW(), true);
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
    def create(cls, xml_file_link, project_id, process_id, version):
        query = f"""INSERT INTO public.process_version
                    (xml_file_link, project_id, process_id, "version", num, last_saved, is_active)
                    VALUES('{xml_file_link}', {project_id}, {process_id}, '{version}',
                        CAST((SELECT CASE WHEN MAX(num) IS NULL THEN 0 ELSE MAX(num) END
                            FROM public.process_version
                            WHERE project_id={project_id} AND process_id={process_id})
                            AS INT)+1,
                    NOW(), false);
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
    def update_version(cls, project_id, process_id, version):
        query = f"""UPDATE public.process_version
                    SET last_saved=NOW()
                    WHERE project_id={project_id} AND process_id={process_id} AND version='{version}';
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
    def get_all(cls):
        query = f"""SELECT xml_file_link, project_id, process_id, "version", num, last_saved
                    FROM public.process_version;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    [
                        "xml_file_link",
                        "project_id",
                        "process_id",
                        "version",
                        "num",
                        "last_saved",
                    ],
                    result,
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_version(cls, project_id, process_id, version):
        query = f"""SELECT xml_file_link, "version", num, last_saved, is_active
                    FROM public.process_version
                    WHERE project_id={project_id} AND process_id={process_id} AND version='{version}';
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result is None:
                    raise Exception("version doesn't exist")
                return dict(
                    zip(
                        ["xml_file_link", "version", "num", "last_saved", "is_active"],
                        result,
                    )
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_by_process(cls, project_id, process_id):
        query = f"""SELECT xml_file_link, "version", num, last_saved
                    FROM public.process_version
                    WHERE project_id={project_id} AND process_id={process_id}
                    ORDER BY last_saved DESC;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                if result is None:
                    raise Exception("version doesn't exist")
                return list_tuple_to_dict(
                    ["xml_file_link", "version", "num", "last_saved"], result
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete(cls, project_id, process_id, version):
        query = f"""DELETE FROM public.process_version
                    WHERE version='{version}' AND project_id={project_id} AND process_id={process_id}
                    RETURNING xml_file_link;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                updated_row = cursor.rowcount
                if updated_row == 0:
                    raise Exception("version doesn't exist")
                connection.commit()
                return cursor.fetchone()[0]
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete_by_process(cls, project_id, process_id):
        query = f"""DELETE FROM public.process_version
                    WHERE AND project_id={project_id} AND process_id={process_id}
                    RETURNING xml_file_link;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                updated_row = cursor.rowcount
                if updated_row == 0:
                    raise Exception("version doesn't exist")
                connection.commit()
                return cursor.fetchall()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete_oldest_version(cls, project_id, process_id):
        query = f"""DELETE FROM public.process_version
                    WHERE project_id={project_id} AND process_id={process_id}
                        AND last_saved=(SELECT MIN(last_saved) FROM public.process_version 
                        WHERE project_id={project_id} AND process_id={process_id});
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
    def get_all_active_process_versions_in_workspace(cls, project_id):
        session = DatabaseConnector.get_session()
        try:
            active_process_versions = (
                session.query(Process_version_model)
                .filter(
                    Process_version_model.project_id == project_id,
                    Process_version_model.is_active == True,
                )
                .all()
            )
            session.commit()
            return active_process_versions
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def activate_process_version(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Process_version_model)
                .filter(Process_version_model.version == process_version_version)
                .first()
            )
            process_version.is_active = True
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_all_process_versions_in_process(cls, process_id):
        session = DatabaseConnector.get_session()
        try:
            process_versions = (
                session.query(
                    Process_version_model.project_id,
                    Process_version_model.version,
                    Process_version_model.process_id,
                    Process_version_model.is_active,
                    Process_version_model.num,
                    Health_model.total_score.label("health"),
                    Strategic_importance_model.total_score.label(
                        "strategic_importance"
                    ),
                    Feasibility_model.total_score.label("feasibility"),
                )
                .outerjoin(
                    Health_model,
                    Process_version_model.version
                    == Health_model.process_version_version,
                )
                .outerjoin(
                    Strategic_importance_model,
                    Process_version_model.version
                    == Strategic_importance_model.process_version_version,
                )
                .outerjoin(
                    Feasibility_model,
                    Process_version_model.version
                    == Feasibility_model.process_version_version,
                )
                .filter(Process_version_model.process_id == process_id)
                .all()
            )
            session.commit()
            return process_versions
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def deactivate_process_version(cls, version):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Process_version_model)
                .filter(Process_version_model.version == version)
                .first()
            )
            process_version.is_active = False
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_current_active_process_version_in_process(cls, process_id):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Process_version_model)
                .filter(
                    Process_version_model.process_id == process_id,
                    Process_version_model.is_active == True,
                )
                .first()
            )
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_process_version_with_smallest_num(cls, process_id):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Process_version_model)
                .filter(Process_version_model.process_id == process_id)
                .order_by(Process_version_model.num)
                .first()
            )
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)
