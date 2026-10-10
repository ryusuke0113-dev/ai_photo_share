# 実装タスク

- 上から順に1つずつ実装する（ルールは `docs/ai_context.md` の「AI の作業ルール」）
- ユーザーがブラウザで確認して「OK」と伝えたら、`[ ]` を `[x]` にする
- 起動コマンド: `python app.py`（ブラウザで http://127.0.0.1:8000 を開く）

## フェーズ 1: 準備

### [ ] T-01 パッケージ一覧のファイル名を変更する

- 対象: `requirement.txt` → `requirements.txt`
- 内容: ファイル名だけを変更する（中身はそのまま）
- 確認: `pip install -r requirements.txt` がエラーなく終わる

### [ ] T-02 最小限の Flask アプリを作る

- 対象: `.env`、`app.py`
- 内容
  - `.env` に `SECRET_KEY` を書く（ランダムな長い文字列）
  - `app.py` で Flask アプリを作り、`SECRET_KEY` を環境変数から読み込む
  - `/`（`index`）は仮の文字（例: 「写真共有アプリ」）を返すだけ
- 確認: 起動して http://127.0.0.1:8000 に仮の文字が表示される

### [ ] T-03 データベースと User モデルを作る

- 対象: `models.py`、`app.py`
- 内容
  - `models.py` に `SqliteDatabase`（`app.db`、外部キー有効）、`BaseModel`、`User`（`UserMixin` を継承）を作る
  - テーブル作成用の関数を作り、`app.py` の起動時に呼ぶ
  - リクエストごとに接続・切断する処理を `app.py` に入れる
  - `Post` は T-10、`Like` は T-15 で追加する
- 対応: `docs/database.md` の `users`
- 確認: 起動するとプロジェクト直下に `app.db` が作られ、エラーが出ない

### [ ] T-04 共通レイアウトと仮のトップページを作る

- 対象: `templates/base.html`、`templates/index.html`、`app.py`
- 内容
  - `base.html` に Bootstrap 5（CDN）、ヘッダー（アプリ名・メニュー）、`flash` メッセージ表示欄を作る
  - `index` を `index.html`（仮の文字だけ）を表示する形に変える
  - `static/css/style.css` は、Bootstrap で足りない見た目が出てきたときに作る
- 確認: トップページにヘッダーと仮の文字が、Bootstrap の見た目で表示される

## フェーズ 2: ユーザー登録・ログイン（Flask-Login・Flask-WTF）

T-03〜T-09 は、認証機能としてまとめて実装済み（ユーザーの確認待ち）。

### [ ] T-05 ユーザー登録画面を表示する

- 対象: `forms.py`、`templates/register.html`、`app.py`
- 内容: `forms.py` に `RegisterForm` を作り、`GET /register`（`register`）でメールアドレス・表示名・パスワードのフォームを表示する
- 対応: F-01、S-04
- 確認: メニューの「登録」から登録画面が表示される

### [ ] T-06 ログイン画面を表示する

- 対象: `forms.py`、`templates/login.html`、`app.py`
- 内容: `forms.py` に `LoginForm` を作り、`GET /login`（`login`）でメールアドレス・パスワードのフォームを表示する
- 対応: F-05、S-05
- 確認: メニューの「ログイン」からログイン画面が表示される。登録画面とログイン画面を相互にリンクで移動できる

### [ ] T-07 ユーザー登録の処理を作る

- 対象: `app.py`、`forms.py`、`templates/register.html`
- 内容
  - `CSRFProtect` を設定し、すべての POST に CSRF 対策をかける
  - `POST /register` で `form.validate_on_submit()` を使って入力をチェックし、パスワードをハッシュ化して `User` を保存する
  - チェック: 未入力、メールアドレスの形式、表示名が 30 文字超、パスワードが 8 文字未満、メールアドレス重複、表示名重複
  - 成功: 成功メッセージを出して `/login` へリダイレクト
  - 失敗: 各入力欄の下にエラーを出して登録画面を再表示（入力したメールアドレス・表示名は残す）
- 対応: F-02〜F-04
- 確認
  - 正しく入力すると、ログイン画面に移って成功メッセージが出る
  - 未入力・形式の違うメールアドレス・31 文字以上の表示名・7 文字以下のパスワード・登録済みのメールアドレス・登録済みの表示名で、それぞれエラーメッセージが出る

### [ ] T-08 ログインの処理を作る

- 対象: `app.py`、`templates/login.html`
- 内容
  - `LoginManager` と `user_loader` を設定する
  - `POST /login` でメールアドレスとパスワードを確認し、成功したら `login_user(user)` でログイン状態にする
  - 成功: `/` へリダイレクト。失敗: 「メールアドレスまたはパスワードが違います」を出してログイン画面を再表示
- 対応: F-06、F-07
- 確認
  - 正しく入力するとトップページに移る
  - パスワードを間違えるとエラーメッセージが出る

### [ ] T-09 ログアウトとメニューの切り替えを作る

- 対象: `app.py`、`templates/base.html`
- 内容
  - `POST /logout`（`logout`）で `logout_user()` を呼んで `/` へリダイレクト（メニューのボタンは CSRF トークン付きの POST フォーム）
  - メニューを、ログイン中は「表示名」「ログアウト」、未ログイン時は「登録」「ログイン」に切り替える
  - 「投稿する」は T-10 でメニューに追加する
- 対応: F-08、F-09
- 確認: ログインするとメニューに表示名が出て、ログアウトすると元のメニューに戻る

## フェーズ 3: 投稿

### [ ] T-10 投稿作成画面を作る

- 対象: `models.py`、`forms.py`、`app.py`、`templates/post_new.html`、`templates/base.html`
- 内容
  - `models.py` に `Post` を追加し、テーブル作成の対象に加える
  - `forms.py` に `PostForm`（`image`、`caption`）を作る
  - `GET /posts/new`（`post_new`）に `flask_login` の `@login_required` を付け、写真とキャプションのフォームを表示する（`enctype="multipart/form-data"`）
  - メニューのログイン中の項目に「投稿する」（`post_new`）を追加する
- 対応: F-10、F-14、S-03
- 確認
  - ログイン中は「投稿する」から投稿作成画面が表示される
  - ログアウトした状態で http://127.0.0.1:8000/posts/new を開くと、ログイン画面に移る

### [ ] T-11 投稿の保存処理を作る

- 対象: `app.py`、`forms.py`、`.gitignore`、`templates/post_new.html`
- 内容
  - `.gitignore` に `uploads/` を追加する
  - `PostForm` に入力チェックを付ける（`flask_wtf.file` の `FileRequired`・`FileAllowed`、キャプションの `Length`）
  - 起動時にプロジェクト直下の `uploads/` がなければ作る
  - `MAX_CONTENT_LENGTH` を 5MB にし、超えた場合（413）はメッセージを出して投稿作成画面へ戻す
  - `POST /posts/new` で入力をチェックし、写真を `uuid` のファイル名で `uploads/` に保存して、`Post` を保存する
  - チェック: 写真が選ばれていない、JPG・PNG 以外、キャプションが 140 文字超
  - 成功: 成功メッセージを出して `/` へリダイレクト
- 対応: F-11〜F-13
- 確認
  - JPG・PNG を投稿すると、トップページに移り、`uploads/` に写真ファイルが増えている
  - キャプションが空欄でも投稿できる
  - 写真なし・GIF などの別形式・141 文字以上のキャプションで、それぞれエラーメッセージが出る
  - 5MB を超える写真でエラーメッセージが出る（開発用サーバーでは、接続エラーの画面になる場合もある）

### [ ] T-12 投稿一覧を作る

- 対象: `app.py`、`templates/index.html`
- 内容
  - `GET /uploads/<filename>`（`uploaded_file`）で、`uploads/` の写真を `send_from_directory` で返す
  - `index` で投稿を新しい順に取得し（`User` を `join`）、縦1列で表示する
  - 表示項目: 写真、キャプション、投稿者の表示名、投稿日時（`2026年10月10日 14:30` の形）
  - 投稿が0件なら「まだ投稿がありません」と表示する
- 対応: F-15〜F-17、S-01
- 確認
  - 投稿した写真が新しい順に表示される
  - ログアウトした状態でも一覧が見られる
  - `app.db` を削除して起動し直すと「まだ投稿がありません」と表示される

### [ ] T-13 投稿詳細を作る

- 対象: `app.py`、`templates/post_detail.html`、`templates/index.html`
- 内容
  - `GET /posts/<int:post_id>`（`post_detail`）で1件の投稿を表示する。存在しなければ 404
  - 一覧の写真をクリックすると詳細へ移るリンクを付ける
  - 詳細画面に「一覧へ戻る」リンクを付ける
- 対応: F-18〜F-20、S-02
- 確認
  - 一覧の写真をクリックすると、その投稿の詳細が表示される
  - http://127.0.0.1:8000/posts/9999 を開くと 404 になる

### [ ] T-14 投稿の削除を作る

- 対象: `app.py`、`templates/post_detail.html`
- 内容
  - 詳細画面で、自分の投稿のときだけ「削除」ボタン（POST のフォーム）を表示する
  - `POST /posts/<int:post_id>/delete`（`post_delete`）は `login_required`。投稿がなければ 404、投稿者でなければ 403
  - 成功: 写真ファイルと `Post` を削除し、成功メッセージを出して `/` へリダイレクト
- 対応: F-21〜F-23
- 確認
  - 自分の投稿の詳細にだけ「削除」ボタンが出る
  - 削除すると一覧から消え、`uploads/` の写真ファイルも消えている
  - 別のユーザーでログインし、他人の投稿の詳細に「削除」ボタンが出ない

## フェーズ 4: いいね（必須機能がすべて完了してから）

### [ ] T-15 いいねのモデルといいね数の表示を作る

- 対象: `models.py`、`templates/post_detail.html`、`app.py`
- 内容
  - `models.py` に `Like` を追加する（`user` + `post` の組み合わせはユニーク、`post` は `on_delete='CASCADE'`）
  - テーブル作成の対象に `Like` を追加する
  - 詳細画面に、その投稿のいいね数を表示する
- 対応: F-25、F-28、`docs/database.md` の `likes`
- 確認: 詳細画面に「いいね 0」と表示される

### [ ] T-16 いいね・取り消しを作る

- 対象: `app.py`、`templates/post_detail.html`
- 内容
  - 詳細画面に「いいね」ボタン（POST のフォーム）を表示する。ログイン中だけ押せる
  - `POST /posts/<int:post_id>/like`（`post_like`）は `login_required`。未いいねなら追加、いいね済みなら取り消す
  - 処理後は同じ投稿の詳細へリダイレクト
- 対応: F-24、F-26、F-27
- 確認
  - 押すといいね数が1増え、もう一度押すと1減る
  - 別のユーザーでログインすると、それぞれ1回ずついいねできる
  - いいねされた投稿を削除してもエラーにならない
