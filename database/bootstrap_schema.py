import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.models.meta_data import Base
from database.db import DatabaseConnector


def import_all_model_modules() -> None:
    models_dir = PROJECT_ROOT / "data" / "models"

    for path in models_dir.rglob("*.py"):
        if path.name.startswith("__"):
            continue
        rel = path.relative_to(PROJECT_ROOT).with_suffix("")
        module_name = ".".join(rel.parts)
        importlib.import_module(module_name)


def bootstrap_schema() -> None:
    import_all_model_modules()
    engine = DatabaseConnector.get_engine()
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.join_workspace (
                memberId integer NOT NULL,
                workspaceId integer NOT NULL,
                joinedAt timestamp without time zone NOT NULL,
                leftAt timestamp without time zone,
                permission text,
                isDeleted boolean,
                isWorkspaceDeleted boolean,
                PRIMARY KEY (memberId, workspaceId)
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.recent_opened_workspace (
                userId integer NOT NULL,
                workspaceId integer NOT NULL,
                openedAt timestamp without time zone NOT NULL,
                isHided boolean,
                isPinned boolean,
                isUserDeletedFromWorkspace boolean,
                PRIMARY KEY (userId, workspaceId)
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.document_file (
                id serial,
                document_link character varying NOT NULL UNIQUE,
                project_id integer NOT NULL,
                last_saved timestamp without time zone,
                PRIMARY KEY (document_link, project_id)
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.work_on (
                id serial,
                user_id integer NOT NULL,
                project_id integer NOT NULL,
                role integer NOT NULL,
                isDeleted boolean,
                leftAt timestamp without time zone,
                PRIMARY KEY (user_id, project_id)
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.request (
                id serial PRIMARY KEY,
                type text,
                content text,
                createdAt timestamp without time zone NOT NULL,
                status text,
                deletedAt timestamp without time zone,
                isDeleted boolean,
                isWorkspaceDeleted boolean,
                workspaceId integer NOT NULL,
                senderId integer NOT NULL,
                handlerId integer,
                recipientId integer NOT NULL,
                fr_permission text,
                to_permission text,
                rcp_permission text
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.notification (
                id serial PRIMARY KEY,
                userId integer NOT NULL,
                createdAt timestamp without time zone NOT NULL,
                deletedAt timestamp without time zone,
                content text,
                isDeleted boolean,
                isStarred boolean,
                isRead boolean,
                notificationType text,
                status text,
                workspaceId integer,
                permission text
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.comment_on (
                id serial PRIMARY KEY,
                user_id integer NOT NULL,
                project_id integer NOT NULL,
                process_id integer NOT NULL,
                xml_file_link character varying NOT NULL,
                content character varying NOT NULL,
                create_at timestamp without time zone
            );
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS public.history_image (
                id serial,
                xml_file_link character varying NOT NULL,
                project_id integer NOT NULL,
                process_id integer NOT NULL,
                save_at timestamp without time zone NOT NULL,
                image_link character varying NOT NULL,
                PRIMARY KEY (id, xml_file_link, project_id, process_id, save_at)
            );
            """
        )
        connection.exec_driver_sql(
            """
            ALTER TABLE IF EXISTS public.process_version
            ADD COLUMN IF NOT EXISTS last_saved timestamp without time zone;
            """
        )
        connection.exec_driver_sql(
            """
            ALTER TABLE IF EXISTS public.process_version
            ADD COLUMN IF NOT EXISTS is_active boolean DEFAULT false;
            """
        )
        connection.exec_driver_sql(
            """
            ALTER TABLE IF EXISTS public.workspace
            ADD COLUMN IF NOT EXISTS targeted_cycle_time double precision DEFAULT 0,
            ADD COLUMN IF NOT EXISTS worst_cycle_time double precision,
            ADD COLUMN IF NOT EXISTS targeted_cost double precision DEFAULT 0,
            ADD COLUMN IF NOT EXISTS worst_cost double precision,
            ADD COLUMN IF NOT EXISTS targeted_quality double precision DEFAULT 100,
            ADD COLUMN IF NOT EXISTS worst_quality double precision DEFAULT 0,
            ADD COLUMN IF NOT EXISTS targeted_flexibility double precision DEFAULT 100,
            ADD COLUMN IF NOT EXISTS worst_flexibility double precision DEFAULT 0;
            """
        )
    print("Schema bootstrap completed.")


if __name__ == "__main__":
    bootstrap_schema()
