# ルーティング設計書

`docs/requirements.md` と `docs/screens.md` を前提としたルーティング設計です。

## 1. ルート一覧

| URL | メソッド | 関数名 | 処理 | ログイン | 成功時の結果 |
| --- | --- | --- | --- | --- | --- |
| `/` | GET | `index` | 投稿一覧を表示 | 不要 | `index.html` を表示 |
| `/posts/<int:post_id>` | GET | `post_detail` | 投稿詳細を表示 | 不要 | `post_detail.html` を表示 |
| `/posts/new` | GET | `post_new` | 投稿作成フォームを表示 | **必要** | `post_new.html` を表示 |
| `/posts/new` | POST | `post_new` | 投稿を保存 | **必要** | `/` へリダイレクト |
| `/posts/<int:post_id>/delete` | POST | `post_delete` | 投稿を削除 | **必要** | `/` へリダイレクト |
| `/register` | GET | `register` | 登録フォームを表示 | 不要 | `register.html` を表示 |
| `/register` | POST | `register` | ユーザーを登録 | 不要 | `/login` へリダイレクト |
| `/login` | GET | `login` | ログインフォームを表示 | 不要 | `login.html` を表示 |
| `/login` | POST | `login` | ログイン処理 | 不要 | `/` へリダイレクト |
| `/logout` | GET | `logout` | ログアウト | 不要 | `/` へリダイレクト |
| `/posts/<int:post_id>/like` | POST | `post_like` | いいね／取り消し（余裕があれば） | **必要** | `/posts/<post_id>` へリダイレクト |

- 関数名は、テンプレートで `url_for('関数名')` と書くときに使う名前です。
- GET と POST が同じ URL のものは、1つの関数で `methods=["GET", "POST"]` として処理します。

## 2. 各ルートの詳細

### `/`（index）

- 投稿を投稿日時の新しい順に取得し、`index.html` に渡す

### `/posts/<int:post_id>`（post_detail）

- 指定された ID の投稿を取得し、`post_detail.html` に渡す
- 投稿が存在しない場合は 404 エラーにする
- ログイン中のユーザーが投稿者かどうかで「削除」ボタンの表示を切り替える

### `/posts/new`（post_new）

- GET: 投稿作成フォームを表示する
- POST: 入力をチェックして保存する
  - 成功: 写真を保存し、投稿をデータベースに保存して `/` へリダイレクト
  - 失敗: エラーメッセージを表示し、`post_new.html` を再表示
- チェック内容: 写真があるか、JPG・PNG か、5MB 以下か、キャプションが 140 文字以下か

### `/posts/<int:post_id>/delete`（post_delete）

- POST のみ（GET では削除しない）
- 投稿が存在しない場合は 404 エラーにする
- ログイン中のユーザーが投稿者でない場合は 403 エラーにする
- 成功: データベースの投稿と写真ファイルを削除して `/` へリダイレクト

### `/register`（register）

- GET: 登録フォームを表示する
- POST: 入力をチェックして保存する
  - 成功: パスワードをハッシュ化してユーザーを保存し、`/login` へリダイレクト
  - 失敗（未入力・メールアドレス重複）: エラーメッセージを表示し、`register.html` を再表示

### `/login`（login）

- GET: ログインフォームを表示する
- POST: メールアドレスとパスワードを確認する
  - 成功: ログイン状態にして `/` へリダイレクト
  - 失敗: エラーメッセージを表示し、`login.html` を再表示

### `/logout`（logout）

- ログイン状態を解除して `/` へリダイレクト

### `/posts/<int:post_id>/like`（post_like）※余裕があれば

- POST のみ
- まだいいねしていなければ追加、いいね済みなら取り消す
- 処理後は `/posts/<post_id>` へリダイレクト

## 3. ログインが必要なルートの扱い

対象: `post_new`、`post_delete`、`post_like`

- 未ログインでアクセスされた場合は `/login` へリダイレクトする
- ログイン後は `/`（投稿一覧）へ移る
- 共通の処理なので、デコレーター（例: `login_required`）にまとめると実装が楽になる

## 4. 写真の表示

- アップロードした写真は `static/uploads/` に保存する
- 写真は Flask の静的ファイル機能で表示するため、専用のルートは作らない
  - 例: テンプレートで `url_for('static', filename='uploads/ファイル名')`

## 5. 実装順のおすすめ

`docs/requirements.md` の第3章と同じ順番です。

1. `/register`
2. `/login`、`/logout`
3. `/posts/new`
4. `/`（投稿一覧）
5. `/posts/<int:post_id>`
6. `/posts/<int:post_id>/delete`
7. `/posts/<int:post_id>/like`（余裕があれば）

ログイン・ログアウト・投稿のあとは `/` へリダイレクトするため、`/` は 2 の時点で「仮のページ」（文字を表示するだけ）を用意しておき、4 で投稿一覧として完成させます。
