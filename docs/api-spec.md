# RAG API 仕様書

## 概要

RAG（Retrieval-Augmented Generation）APIは、ユーザーがMarkdown形式でドキュメントを管理し、質問応答システムとして利用できるAPIです。

## ベースURL

```
http://localhost:8000
```

## 認証

HTTP Basic認証を使用します（`/health`エンドポイント除く）。

```
Authorization: Basic <base64(username:password)>
```

デフォルト認証情報（`.env`で変更可能）:
- Username: `admin`
- Password: `changeme`

## エンドポイント一覧

### 1. ルートエンドポイント

#### GET /
APIの基本情報を取得します。

**認証**: 不要

**レスポンス例**:
```json
{
  "name": "RAG API",
  "version": "0.1.0",
  "description": "Retrieval-Augmented Generation API",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 2. ヘルスチェック

#### GET /health
APIとデータベースの状態を確認します。

**認証**: 不要

**レスポンス例**:
```json
{
  "status": "ok",
  "database": "connected"
}
```

**エラーレスポンス**:
```json
{
  "detail": "Database connection failed: ..."
}
```
Status: `503 Service Unavailable`

---

### 3. 質問応答

#### POST /query
RAGを使用して質問に回答します。

**認証**: 必須

**リクエストボディ**:
```json
{
  "question": "質問内容"
}
```

**レスポンス例**:
```json
{
  "answer": "回答内容がここに表示されます。",
  "sources": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "関連するドキュメントの抜粋（最大500文字）",
      "score": 0.95,
      "metadata": {
        "title": "ドキュメントタイトル",
        "tags": ["tag1", "tag2"]
      }
    }
  ]
}
```

**フィールド説明**:
- `answer`: Gemini 2.5 Proが生成した回答
- `sources`: 回答の根拠となったドキュメント（最大5件）
  - `id`: ドキュメントのUUID
  - `content`: 関連箇所の抜粋
  - `score`: 類似度スコア（0-1、高いほど関連性が高い）
  - `metadata`: ドキュメントのメタデータ

**エラーレスポンス**:
```json
{
  "detail": "Query processing failed: ..."
}
```
Status: `500 Internal Server Error`

---

### 4. ドキュメント管理

#### POST /documents
新しいドキュメントを追加します。

**認証**: 必須

**リクエストボディ**:
```json
{
  "content": "# ドキュメントタイトル\n\n本文の内容...",
  "metadata": {
    "title": "ドキュメントタイトル",
    "tags": ["tag1", "tag2"],
    "author": "作成者名"
  }
}
```

**フィールド説明**:
- `content`: Markdown形式のドキュメント内容（必須）
- `metadata`: 任意のメタデータ（オプション）

**レスポンス例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "# ドキュメントタイトル\n\n本文の内容...",
  "metadata": {
    "title": "ドキュメントタイトル",
    "tags": ["tag1", "tag2"],
    "author": "作成者名"
  },
  "created_at": "2025-10-23T12:34:56.789Z",
  "updated_at": "2025-10-23T12:34:56.789Z"
}
```

Status: `201 Created`

**エラーレスポンス**:
```json
{
  "detail": "Document creation failed: ..."
}
```
Status: `500 Internal Server Error`

---

#### GET /documents
ドキュメント一覧を取得します（ページネーション対応）。

**認証**: 必須

**クエリパラメータ**:
- `skip`: スキップする件数（デフォルト: 0）
- `limit`: 取得する最大件数（デフォルト: 10）

**リクエスト例**:
```
GET /documents?skip=0&limit=10
```

**レスポンス例**:
```json
{
  "total": 42,
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "# ドキュメント1\n\n内容...",
      "metadata": {
        "title": "ドキュメント1"
      },
      "created_at": "2025-10-23T12:34:56.789Z",
      "updated_at": "2025-10-23T12:34:56.789Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "content": "# ドキュメント2\n\n内容...",
      "metadata": {
        "title": "ドキュメント2"
      },
      "created_at": "2025-10-23T13:00:00.000Z",
      "updated_at": "2025-10-23T13:00:00.000Z"
    }
  ]
}
```

**フィールド説明**:
- `total`: ドキュメントの総数
- `documents`: ドキュメントの配列

---

#### GET /documents/{document_id}
特定のドキュメントを取得します。

**認証**: 必須

**パスパラメータ**:
- `document_id`: ドキュメントのUUID

**レスポンス例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "# ドキュメントタイトル\n\n本文の内容...",
  "metadata": {
    "title": "ドキュメントタイトル",
    "tags": ["tag1", "tag2"]
  },
  "created_at": "2025-10-23T12:34:56.789Z",
  "updated_at": "2025-10-23T12:34:56.789Z"
}
```

**エラーレスポンス**:
```json
{
  "detail": "Document with id 550e8400-e29b-41d4-a716-446655440000 not found"
}
```
Status: `404 Not Found`

---

#### DELETE /documents/{document_id}
ドキュメントを削除します。

**認証**: 必須

**パスパラメータ**:
- `document_id`: ドキュメントのUUID

**レスポンス**:
Status: `204 No Content`（成功時はボディなし）

**エラーレスポンス**:
```json
{
  "detail": "Document with id 550e8400-e29b-41d4-a716-446655440000 not found"
}
```
Status: `404 Not Found`

---

## 使用例

### curlでの使用例

#### 1. ヘルスチェック
```bash
curl http://localhost:8000/health
```

#### 2. ドキュメント追加
```bash
curl -X POST http://localhost:8000/documents \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# LangChainとは\n\nLangChainは、大規模言語モデル（LLM）を使用したアプリケーションの開発を支援するフレームワークです。",
    "metadata": {
      "title": "LangChainとは",
      "tags": ["langchain", "llm"]
    }
  }'
```

#### 3. ドキュメント一覧取得
```bash
curl http://localhost:8000/documents?skip=0&limit=10 \
  -u admin:changeme
```

#### 4. 質問応答
```bash
curl -X POST http://localhost:8000/query \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{
    "question": "LangChainとは何ですか？"
  }'
```

#### 5. ドキュメント削除
```bash
curl -X DELETE http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000 \
  -u admin:changeme
```

### Pythonでの使用例

```python
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
auth = HTTPBasicAuth("admin", "changeme")

# ドキュメント追加
response = requests.post(
    f"{BASE_URL}/documents",
    auth=auth,
    json={
        "content": "# FastAPIとは\n\nFastAPIは、Pythonの高速なWebフレームワークです。",
        "metadata": {
            "title": "FastAPIとは",
            "tags": ["fastapi", "python"]
        }
    }
)
print(response.json())

# 質問応答
response = requests.post(
    f"{BASE_URL}/query",
    auth=auth,
    json={
        "question": "FastAPIの特徴は？"
    }
)
print(response.json())
```

## エラーコード一覧

| ステータスコード | 説明 |
|--------------|------|
| 200 OK | リクエスト成功 |
| 201 Created | リソース作成成功 |
| 204 No Content | 削除成功 |
| 401 Unauthorized | 認証失敗 |
| 404 Not Found | リソースが見つからない |
| 500 Internal Server Error | サーバー内部エラー |
| 503 Service Unavailable | サービス利用不可（DB接続エラーなど） |

## 制限事項

- ドキュメントサイズ: 制限なし（ただし、大きすぎるドキュメントは分割推奨）
- 埋め込みベクトル次元: 1536（OpenAI text-embedding-3-small固定）
- 検索結果件数: 最大5件（固定）
- ページネーション: `limit`は最大100件推奨

## 注意事項

1. **API Key**: OpenAI APIキーとGoogle API Keyが必要です
2. **認証情報**: 本番環境では必ず強力なパスワードに変更してください
3. **CORS**: 現在は全オリジン許可（本番環境では適切に設定してください）
4. **レート制限**: 現在実装なし（将来的に追加予定）
