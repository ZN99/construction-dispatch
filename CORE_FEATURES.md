# コア機能ファイルリスト

**バージョン**: 2.1.6
**作成日**: 2025-10-26
**用途**: コア機能のみを抽出して共有・デプロイする際の必須ファイル一覧

---

## 📦 コアファイル分類

このドキュメントは、本システムを最小構成で動作させるために必要な **コアファイル** と、開発・テスト用の **補助ファイル** を分類しています。

---

## 🎯 コア機能ファイル（本番環境必須）

### 1. Django プロジェクト設定

```
construction_dispatch/
├── __init__.py
├── settings.py          # Django設定ファイル
├── urls.py              # ルートURLconf
├── wsgi.py              # WSGIエントリーポイント
└── asgi.py              # ASGIエントリーポイント
```

### 2. 案件管理アプリ (order_management)

```
order_management/
├── __init__.py
├── admin.py                          # 管理画面設定
├── apps.py                           # アプリ設定
├── models.py                         # データモデル（Project, Receipt, Payment等）
├── forms.py                          # フォーム定義
├── urls.py                           # URLルーティング
│
├── views.py                          # 基本ビュー（案件一覧、詳細）
├── views_accounting.py               # 経理・通帳ビュー
├── views_auth.py                     # 認証関連ビュー
├── views_contractor.py               # 業者管理ビュー
├── views_contractor_create.py        # 業者登録ビュー
├── views_contractor_unified.py       # 業者統合ビュー
├── views_cost.py                     # コスト管理ビュー
├── views_landing.py                  # ランディングページビュー
├── views_material.py                 # 資材管理ビュー
├── views_ordering.py                 # 発注管理ビュー
├── views_payment.py                  # 支払管理ビュー
├── views_permission.py               # 権限管理ビュー
├── views_receipt.py                  # 入金管理ビュー
├── views_ultimate.py                 # 統合ダッシュボードビュー
│
├── utils/
│   └── bank_transfer.py              # 銀行振込ユーティリティ
│
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py
│   ├── 0002_project_work_end_completed_and_more.py
│   ├── 0003_project_estimate_not_required.py
│   ├── 0004_progresssteptemplate_projectprogressstep.py
│   ├── 0005_project_additional_items.py
│   ├── 0006_contractor.py
│   ├── 0007_alter_contractor_options.py
│   ├── 0008_project_survey_required_project_survey_status.py
│   ├── 0009_contractor_account_holder_contractor_account_number_and_more.py
│   ├── 0010_fixedcost_variablecost.py
│   ├── 0011_materialorder_materialorderitem.py
│   └── 0012_invoice_invoiceitem.py
│
└── templates/
    └── order_management/
        ├── base.html                         # ベーステンプレート
        ├── dashboard.html                    # 管理ダッシュボード
        ├── ultimate_dashboard.html           # 統合ダッシュボード
        ├── project_list.html                 # 案件一覧
        ├── project_detail.html               # 案件詳細
        ├── project_create.html               # 案件登録
        ├── login.html                        # ログイン画面
        ├── accounting_view.html              # 通帳ビュー
        ├── contractor_list.html              # 業者一覧
        ├── contractor_detail.html            # 業者詳細
        ├── contractor_dashboard.html         # 業者ダッシュボード
        ├── ordering_dashboard.html           # 発注ダッシュボード
        ├── receipt_list.html                 # 入金一覧
        ├── payment_list.html                 # 出金一覧
        └── (その他関連テンプレート)
```

### 3. 現場調査アプリ (surveys)

```
surveys/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                    # Surveyor, Survey, SurveyRoute等
├── urls.py
├── views.py                     # 調査スケジュール、調査員管理
├── forms.py
│
├── migrations/
│   └── (各種マイグレーションファイル)
│
└── templates/
    └── surveys/
        ├── schedule.html                # 調査スケジュール
        ├── surveyor_list.html           # 調査員一覧
        ├── survey_detail.html           # 調査詳細
        └── survey_route_detail.html     # ルート表示（Google Maps）
```

### 4. プロジェクト拡張アプリ (projects)

```
projects/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                         # Surveyor, Survey, MaterialOrder等の拡張モデル
├── forms.py
│
├── craftsman_forms.py                # 職人関連フォーム
├── craftsman_matching.py             # 職人マッチング
├── craftsman_urls.py                 # 職人URL
├── craftsman_views.py                # 職人ビュー
│
├── material_forms.py                 # 資材フォーム
├── material_urls.py                  # 資材URL
├── material_views.py                 # 資材ビュー
│
├── pricing_forms.py                  # 価格設定フォーム
├── pricing_urls.py                   # 価格URL
├── pricing_views.py                  # 価格ビュー
│
├── survey_forms.py                   # 調査フォーム
├── survey_record_forms.py            # 調査記録フォーム
├── survey_urls.py                    # 調査URL
├── survey_views.py                   # 調査ビュー
│
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_surveyor_survey_surveyroute_surveyavailability.py
│   ├── 0003_surveyreport_workernotification_surveytemplate_and_more.py
│   ├── 0004_assignment_craftsman_craftsmanrating_and_more.py
│   ├── 0005_supplier_materialorder.py
│   ├── 0006_projectpricing_projectcost_pricingauditlog.py
│   ├── 0007_constructionprogress_alter_pricingauditlog_options_and_more.py
│   ├── 0008_project_requires_survey.py
│   ├── 0009_add_additional_items_to_progress.py
│   └── 0010_projecteditsession.py
│
└── templates/
    └── projects/
        ├── (職人、資材、価格設定関連テンプレート)
        └── (調査関連テンプレート)
```

### 5. 下請管理アプリ (subcontract_management)

```
subcontract_management/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── urls.py
│
├── migrations/
│   └── (各種マイグレーションファイル)
│
└── templates/
    └── subcontract_management/
        └── (下請関連テンプレート)
```

### 6. 静的ファイル・メディア

```
static/
├── css/
│   └── (カスタムスタイルシート)
├── js/
│   └── (カスタムJavaScript)
└── images/
    └── (ロゴ、アイコン等)

media/
└── (ユーザーアップロード画像、ファイル)

templates/
└── base.html                # グローバルベーステンプレート
```

### 7. ルートファイル

```
manage.py                    # Django管理コマンド
requirements.txt             # Python依存パッケージ
build.sh                     # ビルドスクリプト（Render用）
VERSION.txt                  # バージョン管理
.gitignore                   # Git無視ファイル設定
```

### 8. ドキュメント（推奨）

```
README.md                    # プロジェクト概要
CHANGELOG.md                 # 変更履歴
FUNCTIONAL_REQUIREMENTS.md   # 機能要件定義書（本ドキュメント）
CORE_FEATURES.md             # コア機能リスト（本ドキュメント）
```

---

## 🧪 補助ファイル（開発・テスト・デバッグ用）

### 開発用スクリプト

以下のファイルは **本番環境では不要** です。開発・テスト・データ投入用です。

```
# データ生成・投入スクリプト
initial_data.py                      # 初期データ投入
craftsman_initial_data.py            # 職人データ投入
survey_initial_data.py               # 調査データ投入
create_production_users.py           # 本番ユーザー作成
create_field_surveyor_accounts.py    # 調査員アカウント作成
create_sample_surveys.py             # サンプル調査データ
create_survey_data.py                # 調査データ生成
create_survey_test_data.py           # 調査テストデータ
create_material_data.py              # 資材データ生成
create_payment_data.py               # 支払データ生成
create_payment_variations.py         # 支払バリエーション生成
create_contractor_test_data.py       # 業者テストデータ
create_rental_restoration_data.py    # 賃貸原状回復データ
create_surveyors.py                  # 調査員データ
update_projects.py                   # プロジェクト更新
update_payments_and_variety.py       # 支払更新
populate_progress_steps.py           # 進捗ステップ投入
fix_payment_distribution.py          # 支払配分修正
fix_project_progress.py              # プロジェクト進捗修正

# デバッグ・検証スクリプト
debug_accounting_view.py             # 経理ビューデバッグ
debug_balance_calculation.py         # 残高計算デバッグ
debug_current_month.py               # 当月データデバッグ
debug_detailed_balance.py            # 詳細残高デバッグ
debug_live_balance.py                # ライブ残高デバッグ
debug_transaction_keys.py            # トランザクションキーデバッグ
check_accounting_balance.py          # 経理残高チェック
check_actual_data.py                 # 実データチェック
check_missing_templates.py           # テンプレート欠損チェック
check_progress_count.py              # 進捗カウントチェック
find_project_with_subcontracts.py    # 下請案件検索

# テストスクリプト
test_field_surveyor_system.py        # 調査員システムテスト
test_payment_due_filter.py           # 入金予定フィルタテスト
test_balance_fix.py                  # 残高修正テスト
test_consecutive_profit.py           # 連続利益テスト
test_september_fix.py                # 9月データ修正テスト
final_balance_test.py                # 最終残高テスト

# シェルスクリプト
test_field_surveyor_curl.sh          # 調査員API curlテスト
test_ajax_update.sh                  # Ajax更新テスト
test_update.sh                       # 更新テスト
test_final_update.sh                 # 最終更新テスト

# テンポラリHTMLファイル
error.html                           # エラーページサンプル
response.html                        # レスポンスサンプル
final_response.html                  # 最終レスポンスサンプル
test_final_response.html             # テスト最終レスポンス
test_modal.html                      # モーダルテスト
test_progress_modal.html             # 進捗モーダルテスト

# その他
cookies.txt                          # テスト用クッキー
csrf_token.txt                       # テスト用CSRFトークン
missing_templates_report.json        # テンプレート欠損レポート
demo_html/                           # デモHTML集
demo_html3/                          # デモHTML集（v3）
```

### キャッシュ・一時ファイル

以下は **削除可能** です（.gitignoreに含まれるべき）。

```
__pycache__/                         # Pythonキャッシュ
*.pyc                                # Pythonバイトコード
.DS_Store                            # macOS一時ファイル
db.sqlite3                           # 開発用データベース（本番では永続化）
venv/                                # 仮想環境（本番では別途構築）
staticfiles/                         # collectstatic生成ファイル
```

---

## 📋 コアファイルのみの配布手順

### 方法1: Gitリポジトリから除外

`.gitignore` に以下を追加:

```gitignore
# Development scripts
*_initial_data.py
create_*.py
debug_*.py
check_*.py
test_*.py
fix_*.py
update_*.py
populate_*.py
find_*.py
final_*.py

# Test files
test_*.sh
*.html
!templates/**/*.html
cookies.txt
csrf_token.txt
*.json
demo_html/
demo_html3/

# Python cache
__pycache__/
*.pyc

# Database (if not needed)
db.sqlite3

# Virtual environment
venv/

# Static files (generated)
staticfiles/
```

### 方法2: コアファイルのみをアーカイブ

```bash
# コア機能のみを含むアーカイブを作成
tar -czf construction_dispatch_core.tar.gz \
  construction_dispatch/ \
  order_management/ \
  surveys/ \
  projects/ \
  subcontract_management/ \
  static/ \
  templates/ \
  manage.py \
  requirements.txt \
  build.sh \
  VERSION.txt \
  README.md \
  CHANGELOG.md \
  FUNCTIONAL_REQUIREMENTS.md \
  CORE_FEATURES.md \
  .gitignore
```

### 方法3: コアファイルリストをスクリプトで生成

```bash
#!/bin/bash
# create_core_package.sh

# 必須ディレクトリ
rsync -av --include='*/' \
  --include='construction_dispatch/**' \
  --include='order_management/**' \
  --include='surveys/**' \
  --include='projects/**' \
  --include='subcontract_management/**' \
  --include='static/**' \
  --include='templates/**' \
  --exclude='*' \
  ./ ./core_package/

# 必須ファイル
cp manage.py requirements.txt build.sh VERSION.txt ./core_package/
cp README.md CHANGELOG.md FUNCTIONAL_REQUIREMENTS.md CORE_FEATURES.md ./core_package/
cp .gitignore ./core_package/

echo "Core package created in ./core_package/"
```

---

## 🚀 最小構成でのデプロイ

### 本番環境に必要な最小ファイル

```
construction_dispatch/          # Django設定
order_management/               # 案件管理コア
surveys/                        # 調査機能（オプション）
projects/                       # プロジェクト拡張（オプション）
subcontract_management/         # 下請管理（オプション）
static/                         # 静的ファイル
templates/                      # テンプレート
manage.py                       # Django管理
requirements.txt                # 依存パッケージ
build.sh                        # ビルドスクリプト
VERSION.txt                     # バージョン
```

### デプロイ手順（Render）

1. コアファイルのみをGitリポジトリにプッシュ
2. Renderでリポジトリを連携
3. ビルドコマンド: `./build.sh`
4. 起動コマンド: `gunicorn construction_dispatch.wsgi:application`
5. 環境変数設定:
   - `SECRET_KEY`: Django秘密鍵
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: 本番ドメイン

---

## 📊 ファイル数統計

| カテゴリ | ファイル数（概算） |
|---------|------------------|
| **コアファイル** | 約150ファイル |
| - Pythonモデル/ビュー/フォーム | 50ファイル |
| - テンプレート | 60ファイル |
| - マイグレーション | 30ファイル |
| - 静的ファイル | 10ファイル |
| **補助ファイル** | 約40ファイル |
| - データ生成スクリプト | 20ファイル |
| - デバッグスクリプト | 10ファイル |
| - テストスクリプト | 10ファイル |

**合計**: 約190ファイル（キャッシュ除く）

---

## ✅ チェックリスト

コアファイルのみの配布前に確認:

- [ ] テスト・デバッグスクリプトを除外
- [ ] データ生成スクリプトを除外
- [ ] テンポラリHTMLファイルを除外
- [ ] `__pycache__/` を除外
- [ ] `db.sqlite3` を除外（または初期化）
- [ ] `venv/` を除外
- [ ] `.gitignore` を更新
- [ ] `requirements.txt` を最新化
- [ ] `README.md` を更新
- [ ] マイグレーションファイルを確認
- [ ] 静的ファイルを `collectstatic`
- [ ] 本番環境でテスト起動

---

**管理者**: システム管理チーム
**更新日**: 2025-10-26
**次回レビュー**: 2025-11-26
