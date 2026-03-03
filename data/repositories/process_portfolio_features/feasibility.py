from data.models.process_portfolio_feature_models.process_portfolio_model import (
    Feasibility_model,
)
from database.db import DatabaseConnector


class Feasibility:
    @classmethod
    def check_if_process_version_exists_in_feasibility(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            process_version = (
                session.query(Feasibility_model)
                .filter(
                    Feasibility_model.process_version_version == process_version_version
                )
                .first()
            )
            session.commit()
            return process_version
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_feasibility_of_process_version(
        cls, process_version_version, total_score
    ):
        session = DatabaseConnector.get_session()
        try:
            process_version_feasibility = (
                session.query(Feasibility_model)
                .filter(
                    Feasibility_model.process_version_version == process_version_version
                )
                .first()
            )
            process_version_feasibility.total_score = total_score
            session.commit()
            return process_version_feasibility
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def add_feasibility_of_active_process_version(
        cls, process_version_version, total_score
    ):
        session = DatabaseConnector.get_session()
        try:
            process_version_feasibility = Feasibility_model(
                process_version_version=process_version_version,
                total_score=total_score,
            )
            session.add(process_version_feasibility)
            session.commit()
            return process_version_feasibility
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_feasibility_of_process_version(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            feasibility = (
                session.query(Feasibility_model)
                .filter(
                    Feasibility_model.process_version_version == process_version_version
                )
                .first()
            )
            session.commit()
            return feasibility
        except Exception as e:
            session.rollback()
            raise Exception(e)
