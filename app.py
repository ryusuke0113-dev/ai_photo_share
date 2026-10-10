import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, send_from_directory, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect
from peewee import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, PostForm, RegisterForm
from models import Post, User, create_tables, db

BASE_DIR = Path(__file__).resolve().parent

# python app.py で起動したときも .env を読み込む
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

# 秘密鍵は .env から読み込む（コードに直接書かない）
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# 写真の保存先（static/ の外）と、受け付けるリクエストの最大サイズ（5MB）
app.config["UPLOAD_FOLDER"] = BASE_DIR / "uploads" / "posts"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

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


# 5MB を超えるリクエストは、メッセージを出して投稿作成画面へ戻す
@app.errorhandler(413)
def file_too_large(error):
    flash("ファイルが大きすぎます。5MB 以下の画像を選んでください", "danger")
    return redirect(url_for("post_new"))


# 日時を「2026年10月10日 14:30」の形にする
@app.template_filter("datetime_ja")
def datetime_ja(value):
    return f"{value.year}年{value.month}月{value.day}日 {value:%H:%M}"


# トップページ（投稿一覧。新しい順）
@app.route("/")
def index():
    posts = (
        Post.select(Post, User)
        .join(User)
        .order_by(Post.created_at.desc(), Post.id.desc())
    )
    return render_template("index.html", posts=posts)


# 投稿作成
@app.route("/posts/new", methods=["GET", "POST"])
@login_required
def post_new():
    form = PostForm()

    # 入力チェックに通ったら、写真を安全な名前で保存してから投稿を保存する
    if form.validate_on_submit():
        image = form.image.data
        extension = image.filename.rsplit(".", 1)[-1].lower()
        filename = f"{uuid.uuid4().hex}.{extension}"
        image_path = app.config["UPLOAD_FOLDER"] / filename
        image.save(image_path)

        try:
            Post.create(
                user=current_user.id,
                image_filename=filename,
                caption=form.caption.data or "",
            )
        except IntegrityError:
            image_path.unlink(missing_ok=True)
            flash("投稿の保存に失敗しました。もう一度お試しください", "danger")
            return render_template("post_new.html", form=form)

        flash("投稿しました", "success")
        return redirect(url_for("index"))

    return render_template("post_new.html", form=form)


# uploads/posts/ の写真を返す（static/ の外にあるので専用のルートで配信する）
@app.route("/uploads/posts/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


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

