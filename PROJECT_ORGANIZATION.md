# プロジェクトファイル整理レポート

**プロジェクト名**: 建築派遣管理システム (Construction Dispatch Management System)
**バージョン**: 2.1.6
**作成日**: 2025-10-26
**作成者**: システム分析チーム

---

## 📊 整理サマリー

| カテゴリ | ファイル数 | サイズ | 推奨アクション |
|---------|-----------|--------|---------------|
| **コアファイル（本番必須）** | 約150 | - | 保持・Git管理 |
| **開発・テストスクリプト** | 40 | - | 削除可能（または別ブランチ） |
| **キャッシュ・一時ファイル** | 多数 | 約1MB | 即座に削除 |
| **ドキュメント** | 6 | 約50KB | 保持・更新 |

---

## 🗂️ ファイル整理方針

### 1. 即座に削除すべきファイル

以下のファイルは開発中の一時ファイルで、本番環境には不要です。

#### キャッシュファイル
```bash
# 削除コマンド
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete
```

削除対象:
```
__pycache__/                    # Pythonキャッシュディレクトリ（全階層）
*.pyc                           # Pythonバイトコードファイル
.DS_Store                       # macOS一時ファイル
```

#### テンポラリHTMLファイル
```bash
# 削除推奨
rm error.html
rm response.html
rm final_response.html
rm test_final_response.html
rm test_modal.html
rm test_progress_modal.html
```

削除対象:
```
error.html                      # テスト用エラーページ
response.html                   # テスト用レスポンス
final_response.html             # テスト用最終レスポンス
test_final_response.html        # テスト最終レスポンス
test_modal.html                 # モーダルテスト
test_progress_modal.html        # 進捗モーダルテスト
```

#### テスト用データファイル
```bash
# 削除推奨
rm cookies.txt
rm csrf_token.txt
rm missing_templates_report.json
```

削除対象:
```
cookies.txt                     # テスト用クッキー
csrf_token.txt                  # テスト用CSRFトークン
missing_templates_report.json   # テンプレート欠損レポート
```

#### デモHTMLディレクトリ
```bash
# 削除推奨
rm -rf demo_html/
rm -rf demo_html3/
```

削除対象:
```
demo_html/                      # デモHTML集
demo_html3/                     # デモHTML集（v3）
```

---

### 2. 開発環境のみに残すファイル（別ブランチ推奨）

以下のスクリプトは開発・デバッグ・データ投入に使用しますが、本番環境では不要です。

#### scripts/ ディレクトリに移動を推奨

```
scripts/
├── data_generation/            # データ生成スクリプト
│   ├── initial_data.py
│   ├── craftsman_initial_data.py
│   ├── survey_initial_data.py
│   ├── create_production_users.py
│   ├── create_field_surveyor_accounts.py
│   ├── create_sample_surveys.py
│   ├── create_survey_data.py
│   ├── create_survey_test_data.py
│   ├── create_material_data.py
│   ├── create_payment_data.py
│   ├── create_payment_variations.py
│   ├── create_contractor_test_data.py
│   ├── create_rental_restoration_data.py
│   ├── create_surveyors.py
│   ├── update_projects.py
│   ├── update_payments_and_variety.py
│   ├── populate_progress_steps.py
│   ├── fix_payment_distribution.py
│   └── fix_project_progress.py
│
├── debugging/                  # デバッグスクリプト
│   ├── debug_accounting_view.py
│   ├── debug_balance_calculation.py
│   ├── debug_current_month.py
│   ├── debug_detailed_balance.py
│   ├── debug_live_balance.py
│   ├── debug_transaction_keys.py
│   ├── check_accounting_balance.py
│   ├── check_actual_data.py
│   ├── check_missing_templates.py
│   ├── check_progress_count.py
│   └── find_project_with_subcontracts.py
│
├── testing/                    # テストスクリプト
│   ├── test_field_surveyor_system.py
│   ├── test_payment_due_filter.py
│   ├── test_balance_fix.py
│   ├── test_consecutive_profit.py
│   ├── test_september_fix.py
│   ├── final_balance_test.py
│   ├── test_field_surveyor_curl.sh
│   ├── test_ajax_update.sh
│   ├── test_update.sh
│   └── test_final_update.sh
│
└── README.md                   # スクリプト使用方法
```

#### 移動コマンド例

```bash
# scriptsディレクトリ作成
mkdir -p scripts/{data_generation,debugging,testing}

# データ生成スクリプトを移動
mv *_initial_data.py scripts/data_generation/
mv create_*.py scripts/data_generation/
mv update_*.py scripts/data_generation/
mv populate_*.py scripts/data_generation/
mv fix_*.py scripts/data_generation/

# デバッグスクリプトを移動
mv debug_*.py scripts/debugging/
mv check_*.py scripts/debugging/
mv find_*.py scripts/debugging/

# テストスクリプトを移動
mv test_*.py scripts/testing/
mv test_*.sh scripts/testing/
mv final_balance_test.py scripts/testing/
```

---

### 3. 本番環境に保持すべきコアファイル

以下のファイル・ディレクトリは本番環境で必須です。

#### Djangoプロジェクトコア

```
manage.py                           # Django管理コマンド（必須）
requirements.txt                    # Python依存パッケージ（必須）
build.sh                            # Renderビルドスクリプト（必須）
VERSION.txt                         # バージョン管理（推奨）
.gitignore                          # Git設定（必須）

construction_dispatch/              # Djangoプロジェクト設定（必須）
├── __init__.py
├── settings.py
├── urls.py
├── wsgi.py
└── asgi.py
```

#### アプリケーション

```
order_management/                   # 案件管理アプリ（必須）
├── models.py                       # データモデル
├── views*.py                       # ビュー
├── forms.py                        # フォーム
├── urls.py                         # URL設定
├── admin.py                        # 管理画面
├── migrations/                     # DBマイグレーション
├── templates/                      # HTMLテンプレート
└── utils/                          # ユーティリティ

surveys/                            # 調査機能アプリ（オプション）
├── models.py
├── views.py
├── forms.py
├── urls.py
├── migrations/
└── templates/

projects/                           # プロジェクト拡張アプリ（オプション）
├── models.py
├── *_views.py
├── *_forms.py
├── *_urls.py
├── migrations/
└── templates/

subcontract_management/             # 下請管理アプリ（オプション）
├── models.py
├── views.py
├── urls.py
├── migrations/
└── templates/
```

#### 静的ファイル・テンプレート

```
static/                             # 静的ファイル（CSS, JS, 画像）
├── css/
├── js/
└── images/

templates/                          # グローバルテンプレート
└── base.html

media/                              # ユーザーアップロードファイル（永続化必要）
└── (調査写真、添付ファイル等)
```

#### ドキュメント

```
README.md                           # プロジェクト概要（必須）
CHANGELOG.md                        # 変更履歴（推奨）
FUNCTIONAL_REQUIREMENTS.md          # 機能要件定義書（推奨）
CORE_FEATURES.md                    # コア機能リスト（推奨）
PROJECT_ORGANIZATION.md             # 本ファイル（推奨）
```

---

### 4. データベース・環境ファイル

#### 開発環境

```
db.sqlite3                          # 開発用データベース
                                    # 本番では初期化または別のDB使用
```

#### 本番環境

```
# 環境変数で設定（.envまたはRender環境変数）
SECRET_KEY=<Django秘密鍵>
DEBUG=False
ALLOWED_HOSTS=construction-dispatch.onrender.com
DATABASE_URL=<PostgreSQL URL>       # 本番ではPostgreSQL推奨
```

---

## 📋 実行手順

### ステップ1: キャッシュ削除

```bash
# Pythonキャッシュ削除
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# macOSファイル削除
find . -name ".DS_Store" -delete
```

### ステップ2: テンポラリファイル削除

```bash
# ルートディレクトリのテンポラリHTMLファイル
rm -f error.html response.html final_response.html
rm -f test_final_response.html test_modal.html test_progress_modal.html

# テストデータファイル
rm -f cookies.txt csrf_token.txt missing_templates_report.json

# デモディレクトリ
rm -rf demo_html/ demo_html3/
```

### ステップ3: 開発スクリプトを整理

```bash
# scriptsディレクトリ作成
mkdir -p scripts/{data_generation,debugging,testing}

# データ生成スクリプトを移動
mv *_initial_data.py scripts/data_generation/ 2>/dev/null || true
mv create_*.py scripts/data_generation/ 2>/dev/null || true
mv update_*.py scripts/data_generation/ 2>/dev/null || true
mv populate_*.py scripts/data_generation/ 2>/dev/null || true
mv fix_*.py scripts/data_generation/ 2>/dev/null || true

# デバッグスクリプトを移動
mv debug_*.py scripts/debugging/ 2>/dev/null || true
mv check_*.py scripts/debugging/ 2>/dev/null || true
mv find_*.py scripts/debugging/ 2>/dev/null || true

# テストスクリプトを移動
mv test_*.py scripts/testing/ 2>/dev/null || true
mv test_*.sh scripts/testing/ 2>/dev/null || true
mv final_balance_test.py scripts/testing/ 2>/dev/null || true

echo "スクリプト整理完了"
```

### ステップ4: .gitignore更新

`.gitignore` に以下を追加:

```gitignore
# Python cache
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Database
db.sqlite3
*.db

# Environment
.env
venv/
env/

# Static files (generated)
staticfiles/

# macOS
.DS_Store

# Development scripts
scripts/

# Temporary files
*.html
!templates/**/*.html
!order_management/templates/**/*.html
!surveys/templates/**/*.html
!projects/templates/**/*.html
!subcontract_management/templates/**/*.html
cookies.txt
csrf_token.txt
*.json
!package.json

# Demo files
demo_html/
demo_html3/
```

### ステップ5: Git履歴からも削除（オプション）

```bash
# 過去のコミットからも削除したい場合
git filter-branch --force --index-filter \
  'git rm -rf --cached --ignore-unmatch __pycache__' \
  --prune-empty --tag-name-filter cat -- --all

git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch db.sqlite3' \
  --prune-empty --tag-name-filter cat -- --all
```

### ステップ6: 検証

```bash
# ファイル数確認
echo "=== Pythonファイル数 ==="
find . -name "*.py" | wc -l

echo "=== テンプレート数 ==="
find . -name "*.html" | wc -l

echo "=== 静的ファイル数 ==="
find static/ -type f | wc -l

echo "=== キャッシュ残存確認 ==="
find . -name "*.pyc" -o -name "__pycache__"

echo "=== ルートディレクトリファイル ==="
ls -lh *.py *.sh *.txt *.md 2>/dev/null
```

---

## 📦 コアパッケージ作成スクリプト

### create_core_package.sh

プロジェクトルートに以下のスクリプトを作成:

```bash
#!/bin/bash
# create_core_package.sh - コアファイルのみを抽出してパッケージ化

PACKAGE_DIR="construction_dispatch_core"
ARCHIVE_NAME="construction_dispatch_core_v2.1.6.tar.gz"

echo "=== コアパッケージ作成開始 ==="

# 既存のパッケージディレクトリを削除
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# コアディレクトリをコピー
echo "コアディレクトリをコピー中..."
cp -r construction_dispatch/ "$PACKAGE_DIR/"
cp -r order_management/ "$PACKAGE_DIR/"
cp -r surveys/ "$PACKAGE_DIR/"
cp -r projects/ "$PACKAGE_DIR/"
cp -r subcontract_management/ "$PACKAGE_DIR/"
cp -r static/ "$PACKAGE_DIR/"
cp -r templates/ "$PACKAGE_DIR/"

# 必須ファイルをコピー
echo "必須ファイルをコピー中..."
cp manage.py "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp build.sh "$PACKAGE_DIR/"
cp VERSION.txt "$PACKAGE_DIR/"
cp .gitignore "$PACKAGE_DIR/"

# ドキュメントをコピー
echo "ドキュメントをコピー中..."
cp README.md "$PACKAGE_DIR/"
cp CHANGELOG.md "$PACKAGE_DIR/"
cp FUNCTIONAL_REQUIREMENTS.md "$PACKAGE_DIR/"
cp CORE_FEATURES.md "$PACKAGE_DIR/"
cp PROJECT_ORGANIZATION.md "$PACKAGE_DIR/"

# キャッシュファイルを削除
echo "キャッシュファイルを削除中..."
find "$PACKAGE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PACKAGE_DIR" -name "*.pyc" -delete
find "$PACKAGE_DIR" -name ".DS_Store" -delete

# アーカイブ作成
echo "アーカイブ作成中..."
tar -czf "$ARCHIVE_NAME" "$PACKAGE_DIR"

# ファイル数統計
echo ""
echo "=== 統計情報 ==="
echo "Pythonファイル: $(find "$PACKAGE_DIR" -name "*.py" | wc -l)"
echo "テンプレート: $(find "$PACKAGE_DIR" -name "*.html" | wc -l)"
echo "マイグレーション: $(find "$PACKAGE_DIR/*/migrations" -name "*.py" | wc -l)"
echo "パッケージサイズ: $(du -sh "$PACKAGE_DIR" | cut -f1)"
echo "アーカイブサイズ: $(du -sh "$ARCHIVE_NAME" | cut -f1)"

echo ""
echo "=== 完了 ==="
echo "コアパッケージ: $PACKAGE_DIR"
echo "アーカイブ: $ARCHIVE_NAME"
```

実行:

```bash
chmod +x create_core_package.sh
./create_core_package.sh
```

---

## 📊 Before / After 比較

### Before（整理前）

```
総ファイル数: 約230ファイル
- コアファイル: 150
- 開発スクリプト: 40
- テンポラリファイル: 15
- キャッシュ: 25
- その他: 10

ディレクトリサイズ: 約5MB（db.sqlite3含む）
```

### After（整理後）

```
総ファイル数: 約160ファイル
- コアファイル: 150
- ドキュメント: 6
- 設定ファイル: 4

ディレクトリサイズ: 約2MB（db.sqlite3、scripts/除く）

別管理:
- scripts/data_generation/: 20ファイル
- scripts/debugging/: 10ファイル
- scripts/testing/: 10ファイル
```

---

## ✅ 整理完了チェックリスト

整理作業後に以下を確認してください:

### ファイル削除確認
- [ ] `__pycache__/` ディレクトリが全て削除された
- [ ] `*.pyc` ファイルが全て削除された
- [ ] `.DS_Store` ファイルが全て削除された
- [ ] テンポラリHTMLファイルが削除された
- [ ] テストデータファイル（cookies.txt等）が削除された
- [ ] デモHTMLディレクトリが削除された

### スクリプト整理確認
- [ ] データ生成スクリプトが `scripts/data_generation/` に移動
- [ ] デバッグスクリプトが `scripts/debugging/` に移動
- [ ] テストスクリプトが `scripts/testing/` に移動
- [ ] ルートディレクトリに開発スクリプトが残っていない

### 設定ファイル確認
- [ ] `.gitignore` が更新された
- [ ] 開発スクリプトがGit管理から除外された
- [ ] キャッシュファイルがGit管理から除外された

### ドキュメント確認
- [ ] `README.md` が最新の状態
- [ ] `FUNCTIONAL_REQUIREMENTS.md` が作成された
- [ ] `CORE_FEATURES.md` が作成された
- [ ] `PROJECT_ORGANIZATION.md`（本ファイル）が作成された

### 動作確認
- [ ] `python manage.py runserver` が正常に起動する
- [ ] 主要ページ（ダッシュボード、案件一覧等）が正常に表示される
- [ ] 静的ファイルが正常に読み込まれる
- [ ] データベースマイグレーションが正常に実行できる

### 本番デプロイ準備
- [ ] コアファイルのみがリポジトリに含まれる
- [ ] 環境変数が設定されている
- [ ] `build.sh` が正常に実行できる
- [ ] `collectstatic` が正常に実行できる

---

## 🚀 次のステップ

1. **Git管理の最適化**
   ```bash
   git add .
   git commit -m "プロジェクトファイル整理: コアファイルと開発スクリプトを分離"
   git push origin main
   ```

2. **開発ブランチの作成**
   ```bash
   git checkout -b development
   # scripts/ ディレクトリを追加
   git add scripts/
   git commit -m "開発スクリプトを追加"
   git push origin development
   ```

3. **本番環境デプロイ**
   - Renderで `main` ブランチから自動デプロイ
   - 環境変数を設定
   - データベースマイグレーション実行

4. **継続的なメンテナンス**
   - 定期的に `.gitignore` を見直し
   - 不要なファイルが増えていないか確認
   - ドキュメントを最新に保つ

---

**整理完了日**: 2025-10-26
**次回整理予定**: 2025-11-26
**担当者**: システム管理チーム
