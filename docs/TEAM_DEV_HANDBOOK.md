# チーム開発手順書

## 事前準備

### リポジトリのクローン
```bash
git clone <リポジトリURL>
cd <プロジェクト名>
```

### uvの設定と依存関係のインストール
```bash
uv sync
```

## 作業の流れ（重要）

### 1. 最新のmainブランチを取得
```bash
git checkout main
git pull origin main
```

### 2. 作業ブランチの作成

#### 新機能開発の場合
```bash
git checkout -b feature/機能名
```

#### バグ修正の場合  
```bash
git checkout -b fix/修正内容
```

**ブランチ名の例:**
- `feature/user-login`
- `feature/product-search`
- `fix/header-layout`
- `fix/database-connection`

### 3. 開発環境の起動

#### データベースのマイグレーション実行
```bash
uv run python manage.py migrate
```

#### 開発サーバーの起動
```bash
uv run python manage.py runserver
```

### 4. 開発作業

#### 新しいパッケージが必要な場合
```bash
uv add パッケージ名
```

#### 開発用パッケージの追加
```bash
uv add --dev パッケージ名
```

#### データベースモデルを変更した場合
```bash
# マイグレーションファイルの作成
uv run python manage.py makemigrations

# マイグレーションの実行
uv run python manage.py migrate
```

### 5. コミットとプッシュ

#### 変更をステージング
```bash
git add .
```

#### コミット
```bash
git commit -m "適切なコミットメッセージ"
```

**コミットメッセージの例:**
- `feat: ユーザーログイン機能を追加`
- `fix: ヘッダーレイアウトの崩れを修正`
- `docs: READMEにセットアップ手順を追加`

#### リモートにプッシュ
```bash
git push origin ブランチ名
```

### 6. プルリクエストの作成

1. GitHubでプルリクエストを作成
2. タイトルと説明を記入
3. レビュアーを指定
4. レビュー完了後、mainブランチにマージ

## よく使うコマンド一覧

### Git関連
```bash
# 現在のブランチと状態確認
git status

# ブランチ一覧表示
git branch

# ブランチ切り替え
git checkout ブランチ名

# 変更差分の確認
git diff

# コミット履歴の確認
git log --oneline
```

### Django関連
```bash
# スーパーユーザー作成
uv run python manage.py createsuperuser

# 静的ファイルの収集
uv run python manage.py collectstatic

# シェル起動
uv run python manage.py shell

# テスト実行
uv run python manage.py test
```

## 注意事項

- **mainブランチで直接作業しない**
- **作業前は必ず最新のmainブランチを取得する**
- **コミットメッセージは分かりやすく具体的に書く**
- **大きな変更は小さく分割してコミットする**
- **プルリクエスト作成前にローカルでテストを実行する**
- **ピアレビューを受けてからマージする**

## トラブルシューティング

### コンフリクトが発生した場合
```bash
git pull origin main
# コンフリクトを手動で解決
git add .
git commit -m "コンフリクト解決"
```

### 間違ったブランチで作業してしまった場合
```bash
# 変更を一時保存
git stash

# 正しいブランチに移動
git checkout 正しいブランチ名

# 変更を復元
git stash pop
```