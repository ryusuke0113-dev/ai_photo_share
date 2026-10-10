import os

from flask import Flask

app = Flask(__name__)

# 秘密鍵は .env から読み込む（コードに直接書かない）
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]


# トップページ（今は仮の文字を表示するだけ）
@app.route("/")
def index():
    return "写真共有アプリ"


