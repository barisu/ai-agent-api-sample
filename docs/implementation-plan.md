# RAG API 実装計画

## プロジェクト概要

LangChainとLangGraphを利用したRAG（Retrieval-Augmented Generation）APIの実装。
ユーザーがMarkdown形式でドキュメントを追加し、質問応答システムとして利用できる。

## 技術スタック

### コア技術
- **Python**: 3.12.7
- **パッケージ管理**: uv
- **バージョン管理**: asdf
- **Webフレームワーク**: FastAPI 0.119.1
- **データベース**: PostgreSQL 16 + pgvector 0.8.1

### AI/ML ライブラリ
- **LangChain**: 1.0.2（RAGフレームワーク）
- **LangGraph**: 1.0.1（ワークフロー構築）
- **langchain-google-genai**: 3.0.0（Gemini 2.5 Pro統合）
- **langchain-openai**: 1.0.1（OpenAI Embeddings統合）
- **langchain-postgres**: 0.0.16（PostgreSQLベクトルストア）

### インフラ
- **Docker Compose**: PostgreSQL + pgvectorコンテナ管理
- **認証**: HTTP Basic認証

## プロジェクト構成

```
rag-backend/
├── .tool-versions                 # asdf用Python 3.12設定
├── pyproject.toml                 # uv用プロジェクト設定
├── docker-compose.yml             # PostgreSQL + pgvector
├── init-db.sql                    # DB初期化スクリプト
├── .env.example                   # 環境変数サンプル
├── .gitignore
├── docs/                          # 開発者向けドキュメント
│   ├── implementation-plan.md    # この実装計画
│   ├── api-spec.md              # API仕様書
│   └── setup.md                 # セットアップガイド
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPIアプリケーション
│   ├── config.py                 # 設定管理
│   ├── database.py               # DB接続・セッション管理
│   ├── models.py                 # SQLAlchemyモデル
│   ├── schemas.py                # Pydanticスキーマ
│   ├── auth.py                   # Basic認証
│   ├── dependencies.py           # 依存性注入
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py        # OpenAI Embeddings
│   │   ├── vector_store.py      # pgvector操作
│   │   ├── llm.py               # Gemini 2.5 Pro
│   │   └── chain.py             # RAGチェーン
│   └── api/
│       ├── __init__.py
│       ├── query.py             # 質問応答エンドポイント
│       ├── documents.py         # ドキュメント管理
│       └── health.py            # ヘルスチェック
└── tests/                        # テストコード
```

## データベーススキーマ

### documentsテーブル

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**インデックス:**
- `documents_embedding_idx`: HNSW index for vector similarity search
- `documents_metadata_idx`: GIN index for metadata search

## APIエンドポイント

### 1. ヘルスチェック（認証不要）
```
GET /health
Response: {"status": "ok", "database": "connected"}
```

### 2. 質問応答（Basic認証）
```
POST /query
Request: {"question": "質問内容"}
Response: {
  "answer": "回答内容",
  "sources": [
    {"id": "uuid", "content": "関連箇所", "score": 0.95, "metadata": {...}}
  ]
}
```

### 3. ドキュメント追加（Basic認証）
```
POST /documents
Request: {
  "content": "# タイトル\n\nMarkdown本文...",
  "metadata": {"title": "タイトル", "tags": ["tag1"]}
}
Response: {
  "id": "uuid",
  "content": "...",
  "metadata": {...},
  "created_at": "2025-10-23T...",
  "updated_at": "2025-10-23T..."
}
```

### 4. ドキュメント一覧（Basic認証）
```
GET /documents?skip=0&limit=10
Response: {
  "total": 100,
  "documents": [...]
}
```

### 5. ドキュメント詳細（Basic認証）
```
GET /documents/{id}
Response: {"id": "uuid", "content": "...", ...}
```

### 6. ドキュメント削除（Basic認証）
```
DELETE /documents/{id}
Response: 204 No Content
```

## RAG処理フロー

### ドキュメント追加時
1. ユーザーがMarkdownコンテンツをPOST
2. データベースにドキュメントを保存
3. OpenAI Embeddingsで1536次元ベクトルを生成
4. pgvectorに埋め込みベクトルを保存
5. HNSW indexで高速検索を可能に

### 質問応答時
1. ユーザーの質問を受信
2. 質問文を埋め込みベクトルに変換
3. pgvectorでコサイン類似度による検索（上位5件）
4. 検索結果をコンテキストとしてプロンプトに挿入
5. Gemini 2.5 Proで回答を生成
6. 回答とソースドキュメントを返却

## セキュリティ

### Basic認証
- 全エンドポイント（`/health`除く）でBasic認証必須
- `secrets.compare_digest`でタイミング攻撃を防止
- 環境変数でユーザー名・パスワードを管理

### 環境変数
- `.env`ファイルで管理（`.gitignore`で除外）
- `.env.example`をテンプレートとして提供

## 実装済み機能

### Phase 1: プロジェクト基盤
- ✅ Python 3.12.7のasdf設定
- ✅ uvでのプロジェクト初期化
- ✅ 依存パッケージのインストール
- ✅ Docker Compose構成
- ✅ pgvector拡張の有効化

### Phase 2: データベース層
- ✅ SQLAlchemy設定
- ✅ Documentモデル定義
- ✅ セッション管理
- ✅ Pydanticスキーマ

### Phase 3: 認証
- ✅ Basic認証実装
- ✅ 依存性注入設定

### Phase 4: RAG機能
- ✅ OpenAI Embeddings初期化
- ✅ pgvector操作（追加・検索）
- ✅ Gemini 2.5 Pro初期化
- ✅ RAGチェーン構築

### Phase 5: API
- ✅ ヘルスチェックエンドポイント
- ✅ 質問応答エンドポイント
- ✅ ドキュメント管理エンドポイント
- ✅ FastAPIアプリケーション統合

## 今後の拡張可能性

### LangGraphの活用
現在はシンプルなRAG実装だが、LangGraphを使って以下のような高度なワークフローを実装可能：
- 質問の意図分析と分類
- マルチステップ情報収集
- 回答の検証と改善ループ
- 複数の検索戦略の組み合わせ

### その他の機能拡張
- ストリーミングレスポンス
- ドキュメントの自動分割（チャンキング）
- メタデータによる高度な検索フィルタリング
- ドキュメントの更新機能
- 検索履歴・分析機能
- マルチテナント対応

## 参考資料

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
