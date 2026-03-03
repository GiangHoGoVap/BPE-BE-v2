from data.models.process_portfolio_feature_models.process_portfolio_model import (
    Health_model,
)
from database.db import DatabaseConnector


class Health:
    @classmethod
    def check_if_process_version_exists_in_health(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Health_model)
                .filter(Health_model.process_version_version == process_version_version)
                .first()
            )
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_health_of_process_version(
        cls,
        process_version_version,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
    ):
        session = DatabaseConnector.get_session()
        try:
            process_version_health = (
                session.query(Health_model)
                .filter(Health_model.process_version_version == process_version_version)
                .first()
            )

            if process_version_health:
                if current_cycle_time is not None:
                    process_version_health.current_cycle_time = current_cycle_time
                if current_cost is not None:
                    process_version_health.current_cost = current_cost
                if current_quality is not None:
                    process_version_health.current_quality = current_quality
                if current_flexibility is not None:
                    process_version_health.current_flexibility = current_flexibility
            session.commit()
            return process_version_health
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def add_health_of_process_version(
        cls,
        process_version_version,
        current_cycle_time,
        current_cost,
        current_quality,
        current_flexibility,
    ):
        session = DatabaseConnector.get_session()
        try:
            health = Health_model(
                process_version_version=process_version_version,
                current_cycle_time=current_cycle_time,
                current_cost=current_cost,
                current_quality=current_quality,
                current_flexibility=current_flexibility,
            )
            session.add(health)
            session.commit()
            return health
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_health_of_process_version(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            health = (
                session.query(Health_model)
                .filter(Health_model.process_version_version == process_version_version)
                .first()
            )
            session.commit()
            return health
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def save_total_score(cls, process_version_version, total_score):
        session = DatabaseConnector.get_session()
        try:
            health = (
                session.query(Health_model)
                .filter(Health_model.process_version_version == process_version_version)
                .first()
            )
            if health:
                health.total_score = total_score
            session.commit()
            return health
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def delete_health_values(cls, version):
        session = DatabaseConnector.get_session()
        try:
            health = (
                session.query(Health_model)
                .filter(Health_model.process_version_version == version)
                .first()
            )
            if health:
                session.delete(health)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(e)
