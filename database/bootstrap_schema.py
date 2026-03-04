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
    print("Schema bootstrap completed.")


if __name__ == "__main__":
    bootstrap_schema()
