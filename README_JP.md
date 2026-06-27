# lastfm-client

[English README is here](README.md)

Last.fm Web API の軽量 Python クライアントです。

`lastfm-client` は Last.fm REST API の最小限のラッパーで、オブジェクト指向的な API アクセスではなく、データ収集や研究用途を想定して設計されています。

`pylast` などのライブラリとは異なり、このプロジェクトはレスポンスの解析やデータモデリングを**一切行いません**。すべての API 呼び出しはデコードされた JSON レスポンス（`dict`）をそのまま返すため、利用者がデータを自由に加工・分析・保存できます。

---

## 特徴

* 軽量・依存関係が最小限
* Last.fm Web API の薄いラッパー
* レスポンスを Python の `dict` として返す
* シンプルで予測しやすい API
* リクエストとエラー処理を内蔵
* API キーの環境変数サポート

---

## 対応エンドポイント

### Artist

* `artist.getInfo`
* `artist.search`

### Album

* `album.getInfo`
* `album.search`

### Track

* `track.getInfo`
* `track.search`

上記の 6 エンドポイントのみを意図的にサポートしています。

---

## インストール

```bash
pip install git+https://github.com/W-Yuya/python-minimal-lastfm-client.git
```

またはリポジトリをクローンし、プロジェクトルートを Python パスに追加してください。

---

## 認証

https://www.last.fm/api/account/create で Last.fm の API アカウントを作成し、API キーを取得してください。

クライアントは以下の順序で API キーを探します。

1. コンストラクタへの明示的な引数
2. 環境変数 `LASTFM_API_KEY`

```python
from lastfm_client import LastFMClient

# 環境変数 LASTFM_API_KEY を使用
client = LastFMClient()

# または直接渡す
client = LastFMClient(api_key="your_api_key_here")
```

いずれも指定されていない場合、初期化時に `UsageError` が発生します。

---

## 使い方

### Track

```python
# トラックの詳細情報を取得
track = client.track_get_info(
    artist="Deep Purple",
    track="Smoke on the Water",
)
print(track["track"]["name"])          # "Smoke on the Water"
print(track["track"]["listeners"])     # "1234567"
print(track["track"]["duration"])      # "312000"（ミリ秒）

# トラックを名前で検索
results = client.track_search(track="Smoke on the Water", limit=5)
for item in results["results"]["trackmatches"]["track"]:
    print(item["name"], "-", item["artist"])
```

### Artist

```python
# アーティストの詳細情報を取得
artist = client.artist_get_info("Deep Purple")
print(artist["artist"]["name"])        # "Deep Purple"
print(artist["artist"]["stats"]["listeners"])

# トップタグを表示
for tag in artist["artist"]["tags"]["tag"]:
    print(tag["name"])

# アーティストを名前で検索
results = client.artist_search(artist="Deep Purple", limit=5)
for item in results["results"]["artistmatches"]["artist"]:
    print(item["name"])
```

### Album

```python
# アルバムの詳細情報を取得
album = client.album_get_info(
    artist="Deep Purple",
    album="Machine Head",
)
print(album["album"]["name"])          # "Machine Head"
print(album["album"]["tracks"]["track"][0]["name"])  # 1曲目のタイトル

# アルバムをタイトルで検索
results = client.album_search(album="Machine Head", limit=5)
for item in results["results"]["albummatches"]["album"]:
    print(item["name"], "-", item["artist"])
```

### ページネーション

`artist_search`・`album_search`・`track_search` はいずれも `limit` と `page` パラメータをサポートしています。

```python
# 1ページ目
page1 = client.track_search(track="yesterday", limit=10, page=1)

# 2ページ目
page2 = client.track_search(track="yesterday", limit=10, page=2)
```

---

## 戻り値

すべてのパブリックメソッドは、デコードされた API レスポンスを Python の `dict` として返します。レスポンスの内容に対する追加の解析・変換・バリデーションは一切行われません。

```python
data = client.track_get_info(artist="Deep Purple", track="Smoke on the Water")
# data はただの dict — フィールドに直接アクセスする
print(data["track"]["listeners"])
```

各レスポンスの正確な構造は [Last.fm API ドキュメント](https://www.last.fm/api) に従います。

---

## エラーハンドリング

すべての例外は `LastFMClientError` を継承しています。

```
LastFMClientError
├── UsageError
├── ClientError
│   ├── HTTPError
│   └── APIError
│       ├── AuthenticationError
│       ├── RateLimitError
│       └── NotFoundError
└── ResponseError
```

### UsageError

無効な引数や設定が渡された場合に発生します。ネットワークリクエストが行われる前に送出されます。

```python
from lastfm_client.exceptions import UsageError

try:
    client = LastFMClient()           # API キーが未設定
except UsageError as e:
    print(e)  # "API key not provided. ..."

try:
    client.artist_get_info("")        # 空文字列
except UsageError as e:
    print(e)  # "'artist' must not be empty."

try:
    client.track_search("love", limit=0)  # 無効な limit
except UsageError as e:
    print(e)  # "'limit' must be greater than or equal to 1."
```

### ClientError

Last.fm API との通信に失敗した場合に発生します。

```python
from lastfm_client.exceptions import ClientError, HTTPError

try:
    data = client.artist_get_info("Deep Purple")
except HTTPError as e:
    print(e.status_code, e)           # 例: 503 "Service Unavailable"
except ClientError as e:
    print(e)                          # ネットワークエラー、タイムアウトなど
```

### APIError

Last.fm API がエラーコードを返した場合に発生します。既知のコードは専用のサブクラスに対応付けられています。

```python
from lastfm_client.exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError

try:
    data = client.artist_get_info("Deep Purple")
except AuthenticationError as e:
    print(f"[{e.code}] API キーが無効です")
except NotFoundError as e:
    print(f"[{e.code}] アーティストが見つかりません")
except RateLimitError as e:
    print(f"[{e.code}] レート制限を超過しました")
except APIError as e:
    print(f"[{e.code}] API エラー: {e}")
```

### ResponseError

サーバーが解析できないレスポンスを返した場合に発生します。

```python
from lastfm_client.exceptions import ResponseError

try:
    data = client.artist_get_info("Deep Purple")
except ResponseError as e:
    print(e)                          # "Response is not valid JSON."
```

### すべてのエラーをまとめてキャッチ

```python
from lastfm_client.exceptions import LastFMClientError

try:
    data = client.track_get_info(artist="Deep Purple", track="Smoke on the Water")
except LastFMClientError as e:
    print(f"リクエストに失敗しました: {e}")
```

---

## API エラーコードの対応表

既知の Last.fm API エラーコードは自動的に専用の例外クラスに対応付けられます。

| API コード | 例外クラス            |
| ---------: | --------------------- |
|          4 | `AuthenticationError` |
|          6 | `NotFoundError`       |
|         29 | `RateLimitError`      |

未知のエラーコードは `APIError` として送出されます。対応表は `constants.py` で管理されています。

---

## プロジェクト構成

```
lastfm_client/
├── __init__.py
├── client.py
├── constants.py
└── exceptions.py
```

### client.py

パブリック API を提供します。すべてのパブリックメソッドは引数をバリデートし、内部の `_request()` メソッドに処理を委譲します。`_request()` はネットワーク通信を担い、レスポンスを `_handle_response()` に渡してバリデーションを行います。

### constants.py

プロジェクト全体の定数を管理します。API エンドポイント・デフォルトタイムアウト・ページネーション上限・環境変数名・API エラーコードの対応表などが含まれます。

### exceptions.py

プロジェクト全体で使用するカスタム例外の階層を定義します。

---

## 設計方針

すべてのパブリックメソッドはパラメータを準備し、共通のリクエストハンドラに処理を委譲します。

```
track_get_info()
track_search()

artist_get_info()
artist_search()

album_get_info()
album_search()

        │
        ▼

    _request()

        │
        ▼

 requests.get()

        │
        ▼

_handle_response()
  ├── _handle_http_error()
  ├── response.json()
  └── _handle_api_error()

        │
        ▼

      dict
```

---

## スコープ

このプロジェクトは以下を意図的に**提供しません**。

* オブジェクトモデルや dataclass
* レスポンスのフラット化や変換
* pandas 連携
* キャッシュやリトライ処理
* 非同期リクエスト
* レート制限の管理

このライブラリの唯一の責務は次の通りです。

> **Last.fm REST API → Python `dict`**

それ以外の処理はすべてアプリケーション側に委ねます。

---

## 想定用途

* メタデータ収集
* 音楽情報検索（MIR）
* 研究プロジェクトやデータセット構築
* 探索的分析
* スクリプティング

---

## 開発方針

このプロジェクトは軽量・依存関係最小・予測可能・保守しやすい状態を維持することを目指します。プロジェクトのシンプルさを損なう機能は追加しません。

---

## ライセンス

MIT License.

---

## 免責事項

- このプロジェクトは AI ツール（ChatGPT および Claude）の支援を受けて開発されました。
- Python 3.12.10 にて開発・動作確認済みです。他のバージョンでの動作は保証しません。
- 個人開発プロジェクトのため、積極的なメンテナンスは行っていません。Issue やプルリクエストへの対応が遅れる、または行われない場合があります。
