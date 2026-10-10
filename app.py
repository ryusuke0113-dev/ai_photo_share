import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, url_for
from flask_login import LoginManager, login_user, logout_user
from flask_wtf.csrf import CSRFProtect
from peewee import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, RegisterForm
from models import User, create_tables, db

# python app.py で起動したときも .env を読み込む
load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

# 秘密鍵は .env から読み込む（コードに直接書かない）
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# すべての POST リクエストに CSRF 対策をかける
csrf = CSRFProtect(app)

# ログイン管理（未ログインで @login_required のページを開いたらログイン画面へ）
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "ログインしてください"
login_manager.login_message_category = "danger"

create_tables()


# セッションに保存されたユーザー ID から、ログイン中のユーザーを読み込む
@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id == int(user_id))


# リクエストごとにデータベースへ接続・切断する
@app.before_request
def connect_db():
    db.connect(reuse_if_open=True)


@app.teardown_request
def close_db(exc):
    if not db.is_closed():
        db.close()


# トップページ（今は仮の文字を表示するだけ）
@app.route("/")
def index():
    return render_template("index.html")


# ユーザー登録
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    # 入力チェック（重複チェックを含む）に通ったら保存する
    if form.validate_on_submit():
        try:
            User.create(
                email=form.email.data,
                display_name=form.display_name.data,
                password_hash=generate_password_hash(form.password.data),
            )
        except IntegrityError:
            flash("メールアドレスまたは表示名がすでに使われています", "danger")
            return render_template("register.html", form=form)

        flash("登録が完了しました。ログインしてください", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # メールアドレスとパスワードが正しければログイン状態にする
    if form.validate_on_submit():
        user = User.get_or_none(User.email == form.email.data)
        if user is not None and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("ログインしました", "success")
            return redirect(url_for("index"))

        flash("メールアドレスまたはパスワードが違います", "danger")

    return render_template("login.html", form=form)


# ログアウト（CSRF 対策のため POST のみ受け付ける）
@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("ログアウトしました", "success")
    return redirect(url_for("index"))


# python app.py で起動したとき（開発用サーバー、ポート 8000）
if __name__ == "__main__":
    app.run(port=8000, debug=True)

