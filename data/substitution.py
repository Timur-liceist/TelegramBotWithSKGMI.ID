import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Substitution(SqlAlchemyBase):
    __tablename__ = 'substitutions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.Date)
    number_para = sqlalchemy.Column(sqlalchemy.Integer)
    from_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))