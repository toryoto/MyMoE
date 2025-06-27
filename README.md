# MyMoE (My Management of Employees)

## 環境

- Python 3.13.4
- Django 5.1.7
- uv

## セットアップ

### uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### プロジェクトのセットアップ

```bash
# リポジトリのクローン
git clone <リポジトリURL>
cd <プロジェクト名>

# 仮想環境の作成と有効化
uv venv --python 3.13.4
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env

# データベースのセットアップ
uv run python manage.py migrate

# 開発サーバーの起動
uv run python manage.py runserver
```

## よく使用するコマンド

```bash
# アプリケーションの作成
uv run python manage.py startapp <アプリ名>

# マイグレーション
uv run python manage.py makemigrations
uv run python manage.py migrate

# スーパーユーザー作成
uv run python manage.py createsuperuser

# テスト実行
uv run python manage.py test

# 依存関係の更新
uv pip freeze > requirements.txt
```

## アクセス

- アプリケーション: http://127.0.0.1:8000
- 管理画面: http://127.0.0.1:8000/admin