# コーディングルール

実装はこのルールに従う。ここに書いていないことは、設計書（`docs/`）と Flask・Peewee の一般的な書き方に従う。

## 1. 全般

- PEP 8 に従う（インデントはスペース4つ、文字コードは UTF-8）
- 変数名・関数名は英語の `snake_case`、モデル名は `PascalCase`（`User`、`Post`、`Like`）
- ルートの関数名は `docs/routes.md` のとおりにする（`index`、`post_detail`、`post_new`、`post_delete`、`register`、`login`、`logout`、`post_like`、`uploaded_file`）
- 初学者が読めるように、短く素直に書く。クラスや関数を必要以上に分けない
- 新しいパッケージを追加しない

## 2. コメント

- 日本語で書く
- 関数の前と、処理のまとまり（入力チェック・保存・リダイレクトなど）の前に1行で書く
- 1行ずつの説明は書かない

## 3. ファイルの役割

| ファイル | 書くもの |
| --- | --- |
| `app.py` | Flask アプリの作成、設定、`login_required`、ログインユーザーの読み込み、エラーハンドラー、全ルート、テンプレート用の日時フィルター |
| `models.py` | `db`、`BaseModel`、`User`・`Post`・`Like`、テーブル作成の関数 |

上記以外の `.py` ファイルは、ユーザーの了承なしに作らない。

## 4. 設定（`app.py`）

- パスは `app.py` のあるフォルダを基準に、`pathlib.Path` で組み立てる
- 設定値

| 名前 | 値 |
| --- | --- |
| `SECRET_KEY` | 環境変数 `SECRET_KEY`（`.env`）から読み込む。コードに直接書かない |
| `UPLOAD_FOLDER` | プロジェクト直下の `uploads/`（**`static/` の中ではない**） |
| `MAX_CONTENT_LENGTH` | `5 * 1024 * 1024`（5MB） |
| 許可する拡張子 | `jpg`、`jpeg`、`png`（小文字にして比較する） |

## 5. Flask

- URL は必ず `url_for()` で作る（`"/login"` のように直接書かない）
- POST の処理が成功したら、必ず `redirect()` する（画面を直接返さない）
- 入力エラーのときは、`flash()` でメッセージを出して同じテンプレートを再表示する
- `flash()` のカテゴリーは Bootstrap の色に合わせて `"success"`・`"danger"` を使う
- 404・403 は `abort(404)`・`abort(403)` で返す（専用のエラー画面は作らない）
- 5MB 超（413）だけは、エラーハンドラーで `flash()` を出して投稿作成画面へリダイレクトする
- フォームの値は `request.form.get("名前", "").strip()`、ファイルは `request.files.get("image")` で受け取る
- フォームの `name` は次のとおりにする

| 画面 | `name` |
| --- | --- |
| ユーザー登録 | `email`、`display_name`、`password` |
| ログイン | `email`、`password` |
| 投稿作成 | `image`、`caption` |

## 6. ログイン

- ログイン成功時に `session["user_id"]` にユーザーの `id` を入れる
- `before_request` で `session` からユーザーを読み込み、`g.user` に入れる（未ログインなら `None`）
- ログイン必須のルートには、自作の `login_required` デコレーターを付ける（未ログインなら `flash()` を出して `login` へリダイレクト）
- ログアウトは `session.clear()`
- パスワードは `werkzeug.security` の `generate_password_hash`・`check_password_hash` を使う
- ログイン失敗のメッセージは、メールアドレスとパスワードのどちらが違うか分からないようにする

## 7. Peewee

- 詳細は `docs/database.md` の「Peewee で実装する場合の注意点」に従う
- `SqliteDatabase` は `app.db` の絶対パスと `pragmas={"foreign_keys": 1}` を指定する
- テーブル名は `Meta` の `table_name` で `users`・`posts`・`likes` にする
- 日時の初期値は `default=datetime.datetime.now`（カッコを付けない）
- リクエストごとに `before_request` で `db.connect()`、`teardown_request` で `db.close()` する
- 1件の取得は `get_or_none()` を使い、`None` なら `abort(404)`
- 投稿一覧は `Post.select(Post, User).join(User).order_by(Post.created_at.desc())` の形で取得する
- 重複チェックは保存前に `get_or_none()` で行い、`IntegrityError` は最後の防止策として受け取る
- 文字数のチェックは Flask 側で行う（SQLite は `max_length` をチェックしない）

## 8. 写真

- 保存先はプロジェクト直下の `uploads/`。起動時に `mkdir(exist_ok=True)` で作る
- 保存するファイル名は `uuid.uuid4().hex` + 元の拡張子（小文字）。ユーザーが付けたファイル名は使わない
- 拡張子のチェックはサーバー側で必ず行う
- 表示は `url_for("uploaded_file", filename=post.image_filename)`。`uploaded_file` は `send_from_directory(UPLOAD_FOLDER, filename)` で返す
- 投稿を削除するときは、`Path.unlink(missing_ok=True)` で写真ファイルも削除する

## 9. テンプレート

- すべてのテンプレートは `base.html` を `{% extends %}` で継承し、`{% block title %}` と `{% block content %}` を使う
- Bootstrap 5 は `base.html` で CDN から読み込む。自作の CSS は `static/css/style.css` に最小限だけ書く
- 画面の文言は日本語
- `|safe` は使わない（Jinja2 の自動エスケープに任せる）
- ファイルを送るフォームには `enctype="multipart/form-data"` を付ける
- 削除・いいねは `<form method="post">` のボタンにする（リンクにしない）
- 投稿日時は `app.py` に作った日時フィルターで `2026年10月10日 14:30` の形にする（`f"{dt.year}年{dt.month}月{dt.day}日 {dt:%H:%M}"`）
- メールアドレスは画面に表示しない（表示名を使う）

## 10. 動作確認

- 自動テスト（pytest など）は書かない
- `docs/tasks.md` の「確認」の手順に沿って、ブラウザで手動確認する
- データをリセットしたいときは、サーバーを止めて `app.db` と `uploads/` の中身を削除する

## 11. やらないこと

- 設計書にない機能・画面・ルートの追加
- Flask-Login・Flask-WTF・pytest など、新しいパッケージの追加
- CSRF 対策（今回は対象外）
- 404・403 用の専用テンプレートの作成
- 写真を `static/` の中に保存すること
