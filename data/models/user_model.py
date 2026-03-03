from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.models.meta_data import Base
from database.db import DatabaseConnector


class User_model(Base):
    __tablename__ = "bpe_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    avatar: Mapped[str] = mapped_column(nullable=True)
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    phone: Mapped[str] = mapped_column(nullable=True)


# Base.metadata.create_all(DatabaseConnector.get_engine())
