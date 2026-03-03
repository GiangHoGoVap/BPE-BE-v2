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
    print("Schema bootstrap completed.")


if __name__ == "__main__":
    bootstrap_schema()
