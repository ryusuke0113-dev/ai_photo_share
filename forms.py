from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from models import User

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]

# 拡張子ごとの、ファイル先頭のバイト列（本当にその形式の画像かを確かめるため）
IMAGE_SIGNATURES = {
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "gif": (b"GIF87a", b"GIF89a"),
}


def strip_text(value):
    return value.strip() if value else value


# ユーザー登録フォーム
class RegisterForm(FlaskForm):
    email = EmailField(
        "メールアドレス",
        filters=[strip_text],
        validators=[
            DataRequired(message="メールアドレスを入力してください"),
            Email(message="メールアドレスの形式が正しくありません"),
            Length(max=255, message="メールアドレスは255文字以内で入力してください"),
        ],
    )
    display_name = StringField(
        "表示名",
        filters=[strip_text],
        validators=[
            DataRequired(message="表示名を入力してください"),
            Length(max=30, message="表示名は30文字以内で入力してください"),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードを入力してください"),
            Length(min=8, message="パスワードは8文字以上で入力してください"),
        ],
    )
    submit = SubmitField("登録する")

    # メールアドレスの重複チェック（validate_項目名 は WTForms が自動で呼ぶ）
    def validate_email(self, field):
        if User.get_or_none(User.email == field.data):
            raise ValidationError("このメールアドレスはすでに登録されています")

    # 表示名の重複チェック
    def validate_display_name(self, field):
        if User.get_or_none(User.display_name == field.data):
            raise ValidationError("この表示名はすでに使われています")


# ログインフォーム
class LoginForm(FlaskForm):
    email = EmailField(
        "メールアドレス",
        filters=[strip_text],
        validators=[DataRequired(message="メールアドレスを入力してください")],
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(message="パスワードを入力してください")],
    )
    submit = SubmitField("ログイン")


# 投稿作成フォーム
class PostForm(FlaskForm):
    image = FileField(
        "写真",
        validators=[
            FileRequired(message="写真を選んでください"),
            FileAllowed(ALLOWED_EXTENSIONS, message="png・jpg・jpeg・gif の画像を選んでください"),
        ],
    )
    caption = TextAreaField(
        "キャプション",
        filters=[strip_text],
        validators=[Length(max=140, message="キャプションは140文字以内で入力してください")],
    )

    # 拡張子だけでなく、ファイルの中身が本当にその形式の画像かを確かめる
    def validate_image(self, field):
        extension = field.data.filename.rsplit(".", 1)[-1].lower()
        head = field.data.stream.read(8)
        field.data.stream.seek(0)
        if not head.startswith(IMAGE_SIGNATURES[extension]):
            raise ValidationError("画像ファイルとして読み込めません")
