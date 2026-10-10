import datetime
from pathlib import Path

from flask_login import UserMixin
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, Model, SqliteDatabase

BASE_DIR = Path(__file__).resolve().parent

# SQLite は外部キーが初期設定で無効なので、pragmas で有効にする
db = SqliteDatabase(str(BASE_DIR / "app.db"), pragmas={"foreign_keys": 1})


class BaseModel(Model):
    class Meta:
        database = db


# ユーザー（UserMixin を継承すると Flask-Login で使える）
class User(UserMixin, BaseModel):
    id = AutoField()
    email = CharField(max_length=255, unique=True)
    display_name = CharField(max_length=30, unique=True)
    password_hash = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "users"


# 投稿（写真そのものは uploads/posts/ に保存し、ここにはファイル名だけを保存する）
class Post(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref="posts")
    image_filename = CharField(max_length=255, unique=True)
    caption = CharField(max_length=140, default="")
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "posts"


# テーブルがなければ作成する
def create_tables():
    with db:
        db.create_tables([User, Post])
