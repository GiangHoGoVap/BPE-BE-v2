from data.models.project_model import Project_model
from data.models.user_model import User_model
from data.repositories.utils import *


class Project:
    id = 0
    description = ""
    name = ""
    is_delete = False
    create_at = datetime.now()
    workspaceId = ""
    ownerId = ""
    deletedAt = datetime.now()
    isWorkspaceDeleted = False

    def __init__(self, **kwargs):
        for k in kwargs:
            getattr(self, k)

        vars(self).update(kwargs)

    @classmethod
    def create(
        cls,
        description: str,
        name: str,
        user_id: str,
        createdAt: datetime,
        workspaceId: str,
        is_delete: bool = False,
    ):
        query = f"""
            INSERT INTO public.project(
                description, name, create_at, workspaceId, ownerId, is_delete)
                VALUES ('{description}', '{name}', '{createdAt}', '{workspaceId}', '{user_id}', {is_delete})
                RETURNING id, description, name, create_at, ownerId, workspaceId;
        """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        description,
                        name,
                    ),
                )
                connection.commit()
                result = cursor.fetchone()
                return Project(
                    id=result[0],
                    description=result[1],
                    name=result[2],
                    create_at=result[3],
                    ownerId=result[4],
                    workspaceId=result[5],
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get(cls, project_id):
        query = """SELECT project.id, description, "name", create_at, work_on.user_id, ownerId
                    FROM public.project, public.work_on
                    WHERE project.id=%s AND is_delete=false AND project.id=work_on.project_id;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (project_id,))
                connection.commit()
                result = cursor.fetchone()
                return {
                    "id": result[0],
                    "name": result[1],
                    "description": result[2],
                    "create_at": result[3],
                    "user_id": result[4],
                    "ownerId": result[5],
                }
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def delete(cls, project_id):
        query = """UPDATE public.project
                    SET is_delete=true
                    WHERE id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (project_id,))
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_all(cls):
        query = """SELECT id, description, "name", create_at
                    FROM public.project
                    WHERE is_delete=false;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    ["id", "description", "name", "create_at"], result
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def update_name(cls, project_id, name):
        query = """UPDATE public.project
                    SET "name"=%s
                    WHERE id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        name,
                        project_id,
                    ),
                )
                connection.commit()
                updated_row = cursor.rowcount
                if updated_row == 0:
                    raise Exception("project id incorrect")
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def update_description(cls, project_id, description):
        query = """UPDATE public.project
                    SET description=%s
                    WHERE id=%s;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        description,
                        project_id,
                    ),
                )
                connection.commit()
                updated_row = cursor.rowcount
                if updated_row == 0:
                    raise Exception("project id incorrect")
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_all_project_by_project_ids(cls, project_ids):
        query = f"""SELECT id, description, "name", create_at
                    FROM public.project
                    WHERE id IN ({",".join(str(project_id) for project_id in project_ids)}) AND is_delete=false
                    ORDER BY create_at;
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchall()
                return list_tuple_to_dict(
                    ["id", "description", "name", "create_at"], result
                )
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def getAllProjectsInWorkspace(cls, workspaceId) -> list:
        query = f"""SELECT id
                    FROM public.project
                    WHERE workspaceId='{workspaceId}' AND is_delete=false
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchall()
                return result
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_workspace_id(cls, project_id):
        query = f"""SELECT workspaceId
                    FROM public.project
                    WHERE id={project_id} AND is_delete=false
                """
        connection = DatabaseConnector.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                result = cursor.fetchone()
                return result[0]
        except Exception as e:
            connection.rollback()
            raise Exception(e)

    @classmethod
    def get_all_projects_in_workspace(cls, workspace_id, page, limit):
        session = DatabaseConnector.get_session()
        try:
            result = (
                session.query(
                    Project_model.id,
                    Project_model.name,
                    User_model.name.label("owner_name"),
                )
                .join(User_model, Project_model.ownerid == User_model.id)
                .filter(
                    Project_model.workspaceid == workspace_id,
                    Project_model.is_delete == False,
                )
                .order_by(Project_model.create_at.desc())
                .offset((int(page) - 1 if int(page) - 1 >= 0 else 0) * int(limit))
                .limit(int(limit))
                .all()
            )
            session.commit()
            return result
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_number_of_projects_in_workspace(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            result = (
                session.query(Project_model)
                .filter(Project_model.workspaceid == workspace_id)
                .filter(Project_model.is_delete == False)
                .count()
            )
            session.commit()
            return result
        except Exception as e:
            raise Exception(e)
