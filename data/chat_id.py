import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Chat_id(SqlAlchemyBase):
    __tablename__ = 'chats_id'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.String, unique=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))