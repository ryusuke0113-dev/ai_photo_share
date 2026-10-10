from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from models import User


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
