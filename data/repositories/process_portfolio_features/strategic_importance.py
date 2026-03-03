from data.models.process_portfolio_feature_models.process_portfolio_model import (
    Strategic_importance_model,
)
from database.db import DatabaseConnector


class Strategic_importance:
    @classmethod
    def check_if_process_version_exists_in_strategic_importance(
        cls, process_version_version
    ):
        session = DatabaseConnector.get_session()
        try:
            strategic_importance = (
                session.query(Strategic_importance_model)
                .filter(
                    Strategic_importance_model.process_version_version
                    == process_version_version
                )
                .first()
            )
            session.commit()
            return strategic_importance
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def update_strategic_importance_of_active_process_version(
        cls, process_version_version, total_score
    ):
        session = DatabaseConnector.get_session()
        try:
            process_version_strategic_importance = (
                session.query(Strategic_importance_model)
                .filter(
                    Strategic_importance_model.process_version_version
                    == process_version_version
                )
                .first()
            )
            process_version_strategic_importance.total_score = total_score
            session.commit()
            return process_version_strategic_importance
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def add_strategic_importance_of_active_process_version(
        cls, process_version_version, total_score
    ):
        session = DatabaseConnector.get_session()
        try:
            process_version_strategic_importance = Strategic_importance_model(
                process_version_version=process_version_version,
                total_score=total_score,
            )
            session.add(process_version_strategic_importance)
            session.commit()
            return process_version_strategic_importance
        except Exception as e:
            session.rollback()
            raise Exception(e)

    @classmethod
    def get_strategic_importance_of_process_version(cls, process_version_version):
        session = DatabaseConnector.get_session()
        try:
            strategic_importance = (
                session.query(Strategic_importance_model)
                .filter(
                    Strategic_importance_model.process_version_version
                    == process_version_version
                )
                .first()
            )
            session.commit()
            return strategic_importance
        except Exception as e:
            session.rollback()
            raise Exception(e)
