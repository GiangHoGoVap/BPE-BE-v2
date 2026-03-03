from datetime import datetime

from sqlalchemy import or_

from data.models.process_model import Process_version_model, Process_model
from data.models.process_portfolio_feature_models.process_portfolio_model import (
    Process_portfolio_model,
    Health_model,
    Strategic_importance_model,
    Feasibility_model,
)
from data.models.project_model import Project_model
from database.db import DatabaseConnector


class Process_portfolio:
    @classmethod
    def add_process_portfolio(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = Process_portfolio_model(
                workspace_id=workspace_id, is_deleted=False, created_at=datetime.now()
            )
            session.add(process_portfolio)
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()

    @classmethod
    def check_if_process_portfolio_exists(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = (
                session.query(Process_portfolio_model)
                .filter(Process_portfolio_model.workspace_id == workspace_id)
                .first()
            )
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()

    @classmethod
    def get_active_process_versions(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = (
                session.query(Process_version_model)
                .join(
                    Project_model,
                    Process_version_model.project_id == Project_model.id,
                )
                .filter(
                    Process_version_model.is_active == True,
                    Project_model.workspaceid == workspace_id,
                )
                .first()
            )
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()

    @classmethod
    def get_not_available_process_versions(cls, workspace_id, page, limit):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = (
                session.query(
                    Process_version_model.version,
                    Process_version_model.num,
                    Process_version_model.project_id,
                    Process_version_model.process_id,
                    Process_model.name.label("process_name"),
                    Health_model.total_score.label("health"),
                    Strategic_importance_model.total_score.label(
                        "strategic_importance"
                    ),
                    Feasibility_model.total_score.label("feasibility"),
                )
                .join(
                    Health_model,
                    Process_version_model.version
                    == Health_model.process_version_version,
                )
                .join(
                    Strategic_importance_model,
                    Process_version_model.version
                    == Strategic_importance_model.process_version_version,
                )
                .join(
                    Feasibility_model,
                    Process_version_model.version
                    == Feasibility_model.process_version_version,
                )
                .join(
                    Process_model,
                    Process_version_model.process_id == Process_model.id,
                )
                .join(
                    Project_model,
                    Process_version_model.project_id == Project_model.id,
                )
                .filter(
                    Project_model.workspaceid == workspace_id,
                    Process_version_model.is_active == True,
                    Project_model.is_delete == False,
                    or_(
                        Health_model.total_score == None,
                        Strategic_importance_model.total_score == None,
                        Feasibility_model.total_score == None,
                    ),
                )
                # .order_by(Process_version_model.num.desc())
                .offset((int(page) - 1 if int(page) - 1 >= 0 else 0) * int(limit))
                .limit(int(limit))
                .all()
            )
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()

    @classmethod
    def get_number_of_not_available_process_versions(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = (
                session.query(Process_version_model)
                .join(
                    Health_model,
                    Process_version_model.version
                    == Health_model.process_version_version,
                )
                .join(
                    Strategic_importance_model,
                    Process_version_model.version
                    == Strategic_importance_model.process_version_version,
                )
                .join(
                    Feasibility_model,
                    Process_version_model.version
                    == Feasibility_model.process_version_version,
                )
                .join(
                    Project_model,
                    Process_version_model.project_id == Project_model.id,
                )
                .filter(
                    Project_model.workspaceid == workspace_id,
                    or_(
                        Health_model.total_score == None,
                        Strategic_importance_model.total_score == None,
                        Feasibility_model.total_score == None,
                    ),
                )
                .count()
            )
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()

    @classmethod
    def get_eligible_process_versions(cls, workspace_id):
        session = DatabaseConnector.get_session()
        try:
            process_portfolio = (
                session.query(
                    Process_version_model.version,
                    Process_version_model.num,
                    Project_model.name.label("project_name"),
                    Process_model.name.label("process_name"),
                    Health_model.total_score.label("health"),
                    Strategic_importance_model.total_score.label(
                        "strategic_importance"
                    ),
                    Feasibility_model.total_score.label("feasibility"),
                )
                .join(
                    Health_model,
                    Process_version_model.version
                    == Health_model.process_version_version,
                )
                .join(
                    Strategic_importance_model,
                    Process_version_model.version
                    == Strategic_importance_model.process_version_version,
                )
                .join(
                    Feasibility_model,
                    Process_version_model.version
                    == Feasibility_model.process_version_version,
                )
                .join(
                    Process_model,
                    Process_version_model.process_id == Process_model.id,
                )
                .join(
                    Project_model,
                    Process_version_model.project_id == Project_model.id,
                )
                .filter(
                    Project_model.workspaceid == workspace_id,
                    Health_model.total_score != None,
                    Strategic_importance_model.total_score != None,
                    Feasibility_model.total_score != None,
                    Process_version_model.is_active == True,
                )
                .all()
            )
            session.commit()
            return process_portfolio
        except Exception as e:
            session.rollback()
            raise Exception(e)
        finally:
            session.close()
