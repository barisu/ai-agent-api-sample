# セットアップガイド

## 前提条件

以下のツールがインストールされている必要があります：

- **asdf**: Pythonバージョン管理
- **uv**: Pythonパッケージマネージャー
- **Docker & Docker Compose**: データベースコンテナ管理
- **Git**: バージョン管理

## 1. リポジトリのクローン

```bash
git clone <repository-url>
cd rag-backend
```

## 2. Python環境のセットアップ

### asdfでPython 3.12.7をインストール

```bash
# Pythonプラグインがインストールされていない場合
asdf plugin add python

# Python 3.12.7をインストール
asdf install python 3.12.7
```

`.tool-versions`ファイルで指定されているため、ディレクトリ内では自動的にPython 3.12.7が使用されます。

## 3. uvのインストール

uvがインストールされていない場合：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# または、pipxを使用
pipx install uv
```

## 4. 依存パッケージのインストール

```bash
# プロジェクトの依存関係を同期
uv sync
```

これにより、`.venv`ディレクトリに仮想環境が作成され、必要なパッケージがすべてインストールされます。

## 5. 環境変数の設定

`.env.example`をコピーして`.env`を作成します：

```bash
cp .env.example .env
```

`.env`ファイルを編集し、必要な値を設定します：

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/rag_db

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Basic Authentication
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=changeme

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

**重要**:
- `OPENAI_API_KEY`: [OpenAI Platform](https://platform.openai.com/)で取得
- `GOOGLE_API_KEY`: [Google AI Studio](https://aistudio.google.com/)で取得
- `BASIC_AUTH_PASSWORD`: 本番環境では必ず変更してください

## 6. PostgreSQLのセットアップ

Docker Composeを使用してPostgreSQL + pgvectorを起動します：

```bash
# バックグラウンドで起動
docker compose up -d

# ログを確認
docker compose logs -f

# 起動確認
docker compose ps
```

データベースが正常に起動すると、以下が自動的に実行されます：
- pgvector拡張の有効化
- documentsテーブルの作成
- 必要なインデックスの作成

### データベース接続確認

```bash
# PostgreSQLに接続
docker compose exec postgres psql -U postgres -d rag_db

# pgvectorが有効か確認
\dx

# テーブル確認
\dt

# 終了
\q
```

## 7. アプリケーションの起動

### 開発モード（ホットリロード有効）

```bash
# uvで仮想環境を使用して実行
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

または：

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# uvicornで起動
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 本番モード

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

アプリケーションが起動すると、以下のURLでアクセスできます：

- **API**: http://localhost:8000
- **API ドキュメント（Swagger UI）**: http://localhost:8000/docs
- **API ドキュメント（ReDoc）**: http://localhost:8000/redoc

## 8. 動作確認

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

期待される出力：
```json
{"status": "ok", "database": "connected"}
```

### ドキュメント追加

```bash
curl -X POST http://localhost:8000/documents \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# テストドキュメント\n\nこれはテスト用のドキュメントです。",
    "metadata": {"title": "テスト"}
  }'
```

### 質問応答

```bash
curl -X POST http://localhost:8000/query \
  -u admin:changeme \
  -H "Content-Type: application/json" \
  -d '{"question": "テストドキュメントについて教えて"}'
```

## トラブルシューティング

### PostgreSQL接続エラー

**エラー**: `could not connect to server: Connection refused`

**解決方法**:
```bash
# Dockerコンテナの状態確認
docker compose ps

# コンテナが起動していない場合
docker compose up -d

# ログを確認
docker compose logs postgres
```

### OpenAI API エラー

**エラー**: `AuthenticationError: Incorrect API key provided`

**解決方法**:
- `.env`ファイルの`OPENAI_API_KEY`が正しいか確認
- OpenAI Platformでキーが有効か確認
- APIキーに残高があるか確認

### Gemini API エラー

**エラー**: `Invalid API key`

**解決方法**:
- `.env`ファイルの`GOOGLE_API_KEY`が正しいか確認
- Google AI Studioでキーが有効か確認
- APIキーの利用制限を確認

### 認証エラー

**エラー**: `401 Unauthorized`

**解決方法**:
- Basic認証のユーザー名とパスワードが正しいか確認
- `.env`の`BASIC_AUTH_USERNAME`と`BASIC_AUTH_PASSWORD`を確認

### パッケージインストールエラー

**エラー**: `No solution found when resolving dependencies`

**解決方法**:
```bash
# uvのキャッシュをクリア
uv cache clean

# 再度同期
uv sync
```

### pgvector拡張がない

**エラー**: `extension "vector" is not available`

**解決方法**:
```bash
# PostgreSQLコンテナを再作成
docker compose down -v
docker compose up -d
```

## データベースのリセット

開発中にデータベースをリセットしたい場合：

```bash
# コンテナとボリュームを削除
docker compose down -v

# 再起動
docker compose up -d
```

**注意**: すべてのデータが削除されます。

## 環境別の設定

### 開発環境

- `LOG_LEVEL=DEBUG`: 詳細なログを出力
- `--reload`: コード変更時に自動リロード

### 本番環境

- `LOG_LEVEL=INFO` または `WARNING`
- `--workers 4`: 複数ワーカーで起動
- CORS設定を適切に制限（`src/main.py`を編集）
- 強力なパスワードを設定
- HTTPS/TLSを使用（リバースプロキシ経由推奨）

## 次のステップ

1. [API仕様書](api-spec.md)を確認してAPIの使い方を学ぶ
2. [実装計画](implementation-plan.md)でシステムアーキテクチャを理解する
3. ドキュメントを追加してRAGを試す
4. 質問応答機能をテストする

## 参考リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [asdf Documentation](https://asdf-vm.com/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
