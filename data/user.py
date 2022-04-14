import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    skgmi_id = sqlalchemy.Column(sqlalchemy.String)
    # login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    # password = sqlalchemy.Column(sqlalchemy.String, unique=True)