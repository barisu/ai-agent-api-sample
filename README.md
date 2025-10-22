# RAG API

LangChain、LangGraph、PostgreSQL pgvectorを使用したRAG（Retrieval-Augmented Generation）APIです。
ユーザーがMarkdown形式でドキュメントを管理し、質問応答システムとして利用できます。

## 特徴

- **最新技術スタック**: LangChain 1.0.2、LangGraph 1.0.1、FastAPI 0.119.1
- **高性能RAG**: OpenAI Embeddings + Gemini 2.5 Pro + pgvector
- **Markdown対応**: ドキュメントはMarkdown形式で管理
- **ベクトル検索**: pgvectorのHNSW indexによる高速類似検索
- **Basic認証**: シンプルで安全な認証機構
- **モダンな開発環境**: Python 3.12、uv、asdf、Docker Compose

## クイックスタート

### 前提条件

- Python 3.12（asdfで管理）
- uv（パッケージマネージャー）
- Docker & Docker Compose
- OpenAI API Key
- Google API Key（Gemini用）

### インストール

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd rag-backend
```

2. **Python環境のセットアップ**
```bash
# Python 3.12.7をインストール
asdf install python 3.12.7

# 依存パッケージをインストール
uv sync
```

3. **環境変数の設定**
```bash
# .envファイルを作成
cp .env.example .env

# .envを編集してAPIキーを設定
# OPENAI_API_KEY=your_openai_api_key
# GOOGLE_API_KEY=your_google_api_key
```

4. **PostgreSQLの起動**
```bash
docker compose up -d
```

5. **アプリケーションの起動**
```bash
uv run uvicorn src.main:app --reload
```

APIは http://localhost:8000 で利用可能になります。

## API使用例

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### ドキュメント追加

```bash
curl -X POST http://localhost:8000/documents \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# LangChainとは\n\nLangChainは大規模言語モデルを使用したアプリケーションの開発フレームワークです。",
    "metadata": {"title": "LangChain", "tags": ["ai", "llm"]}
  }'
```

### 質問応答

```bash
curl -X POST http://localhost:8000/query \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{"question": "LangChainとは何ですか？"}'
```

### ドキュメント一覧

```bash
curl http://localhost:8000/documents \
  -u admin:changeme
```

## APIドキュメント

アプリケーション起動後、以下のURLで対話的なAPIドキュメントを参照できます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## プロジェクト構成

```
rag-backend/
├── src/
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py            # 設定管理
│   ├── database.py          # データベース接続
│   ├── models.py            # SQLAlchemyモデル
│   ├── schemas.py           # Pydanticスキーマ
│   ├── auth.py              # Basic認証
│   ├── dependencies.py      # 依存性注入
│   ├── rag/                 # RAG機能
│   │   ├── embeddings.py   # OpenAI Embeddings
│   │   ├── vector_store.py # pgvector操作
│   │   ├── llm.py          # Gemini 2.5 Pro
│   │   └── chain.py        # RAGチェーン
│   └── api/                 # APIエンドポイント
│       ├── health.py
│       ├── query.py
│       └── documents.py
├── docs/                    # 開発者向けドキュメント
│   ├── implementation-plan.md
│   ├── api-spec.md
│   └── setup.md
├── docker-compose.yml       # PostgreSQL + pgvector
├── init-db.sql             # DB初期化スクリプト
├── pyproject.toml          # uvプロジェクト設定
└── .tool-versions          # asdf設定
```

## 技術スタック

### バックエンド
- **Python**: 3.12.7
- **FastAPI**: 0.119.1（Webフレームワーク）
- **SQLAlchemy**: 2.0+（ORM）
- **uvicorn**: ASGI サーバー

### AI/ML
- **LangChain**: 1.0.2（RAGフレームワーク）
- **LangGraph**: 1.0.1（ワークフロー構築）
- **OpenAI Embeddings**: text-embedding-3-small（1536次元）
- **Gemini 2.5 Pro**: 質問応答生成

### データベース
- **PostgreSQL**: 16
- **pgvector**: 0.8.1（ベクトル類似検索）
- **HNSW Index**: 高速近似近傍探索

### 開発ツール
- **uv**: パッケージ管理
- **asdf**: Pythonバージョン管理
- **Docker Compose**: コンテナオーケストレーション

## アーキテクチャ

### RAG処理フロー

1. **ドキュメント追加時**:
   - ユーザーがMarkdownをPOST
   - OpenAI Embeddingsで1536次元ベクトルを生成
   - PostgreSQLに保存（pgvector）

2. **質問応答時**:
   - 質問を埋め込みベクトルに変換
   - pgvectorでコサイン類似度検索（上位5件）
   - 検索結果をコンテキストとしてGemini 2.5 Proに入力
   - 生成された回答とソースを返却

## 開発

### ローカル開発

```bash
# 開発サーバー起動（ホットリロード）
uv run uvicorn src.main:app --reload

# テスト実行（今後実装予定）
uv run pytest

# コードフォーマット
uv run black src/
uv run isort src/
```

### Docker環境

```bash
# PostgreSQL起動
docker compose up -d

# ログ確認
docker compose logs -f postgres

# データベース接続
docker compose exec postgres psql -U postgres -d rag_db

# 停止
docker compose down

# データベースリセット
docker compose down -v
```

## セキュリティ

- **Basic認証**: 全エンドポイント（`/health`除く）で認証必須
- **環境変数**: 機密情報は`.env`で管理（`.gitignore`で除外）
- **タイミング攻撃対策**: `secrets.compare_digest`使用
- **CORS**: 現在は全オリジン許可（本番環境では制限推奨）

## ドキュメント

詳細なドキュメントは[docs/](docs/)ディレクトリを参照してください：

- [セットアップガイド](docs/setup.md) - 詳細なセットアップ手順
- [API仕様書](docs/api-spec.md) - 全エンドポイントの詳細仕様
- [実装計画](docs/implementation-plan.md) - システムアーキテクチャと実装詳細

## トラブルシューティング

### データベース接続エラー

```bash
# PostgreSQLコンテナの状態確認
docker compose ps

# コンテナ再起動
docker compose restart postgres
```

### API Key エラー

- `.env`ファイルのAPIキーが正しいか確認
- OpenAI Platform / Google AI Studioでキーが有効か確認

### 認証エラー

- `.env`の`BASIC_AUTH_USERNAME`と`BASIC_AUTH_PASSWORD`を確認
- デフォルトは `admin` / `changeme`

## 今後の拡張

- [ ] LangGraphを使った高度なワークフロー
- [ ] ストリーミングレスポンス対応
- [ ] ドキュメントの自動チャンキング
- [ ] メタデータによる高度な検索フィルタリング
- [ ] レート制限の実装
- [ ] ユニットテスト・統合テストの追加
- [ ] CI/CDパイプラインの構築

## ライセンス

MIT License

## 貢献

Pull Requestを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。
