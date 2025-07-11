## サービス概要
- 名前：MyMoE
- 概要：社員ごとのプラットフォームを備えた社員管理システム。人事担当者を含む全ての社員が、自身の権限レベルに応じて他の社員の情報を閲覧・管理できる機能を提供します。

## プロジェクト構成

### アプリケーション
- **employees**:
    - 社員情報の管理（登録、更新、削除）
    - ユーザー認証（ログイン、ログアウト、サインアップ）
    - 部署や役職などの基本情報との連携
- **profiles**:
    - 各社員の個人プロフィール設定と表示
    - プロフィール情報の編集機能
    - 他の社員が閲覧できる公開情報の管理
- **departments**:
    - 部署、役職、組織階層などの組織情報の管理
    - 部署ごとの社員一覧表示
    - 組織図の管理

### 全体構成
- **mymoe**: Djangoプロジェクトのメイン設定（settings.py, urls.pyなど）
- **template**: 各アプリケーションで共通利用されるベーステンプレートや、各アプリ固有のHTMLテンプレートを格納
