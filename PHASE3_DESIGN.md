# Phase 3: 進捗管理・レポート機能 - 設計ドキュメント

## 1. 機能概要

### 1.1 進捗管理機能
**目的**: プロジェクトの進捗状況を可視化し、遅延やリスクを早期発見

**主要機能**:
- プロジェクト進捗率の自動計算
- ガントチャート表示
- マイルストーン管理
- 遅延アラート
- 進捗レポート自動生成

### 1.2 レポート生成機能
**目的**: 経営判断に必要なレポートを自動生成

**レポートタイプ**:
1. **月次経営レポート**
   - 売上・利益サマリー
   - プロジェクト進捗状況
   - キャッシュフロー状況
   - 予実対比

2. **プロジェクト別レポート**
   - プロジェクト詳細
   - 原価・利益分析
   - 進捗状況
   - 課題・リスク

3. **キャッシュフローレポート**
   - 入出金予定
   - 売掛金・買掛金一覧
   - 資金繰り表

4. **予測レポート**
   - 売上予測
   - 損益予測
   - シナリオ比較

### 1.3 PDF出力機能
**目的**: レポートをPDF形式で出力し、社内外で共有可能に

**出力形式**:
- A4サイズ
- 日本語対応
- チャート・グラフ埋め込み
- カスタムヘッダー・フッター

## 2. データモデル

### 2.1 ProjectProgress モデル（新規作成）
```python
class ProjectProgress(models.Model):
    """プロジェクト進捗記録"""
    project = ForeignKey(Project)
    recorded_date = DateField  # 記録日
    progress_rate = DecimalField  # 進捗率 (0-100%)
    status = CharField  # ステータス
    notes = TextField  # 備考
    recorded_by = ForeignKey(User)  # 記録者

    # マイルストーン
    milestone_name = CharField
    milestone_date = DateField
    milestone_completed = BooleanField

    # リスク・課題
    has_risk = BooleanField
    risk_description = TextField
    risk_level = CharField  # high, medium, low
```

### 2.2 Report モデル（新規作成）
```python
class Report(models.Model):
    """レポート"""
    REPORT_TYPE_CHOICES = [
        ('monthly', '月次経営レポート'),
        ('project', 'プロジェクト別レポート'),
        ('cashflow', 'キャッシュフローレポート'),
        ('forecast', '予測レポート'),
    ]

    title = CharField  # レポートタイトル
    report_type = CharField  # レポートタイプ
    generated_date = DateTimeField  # 生成日時
    generated_by = ForeignKey(User)  # 生成者

    # 対象期間
    period_start = DateField
    period_end = DateField

    # レポートデータ（JSON）
    report_data = JSONField

    # PDF保存
    pdf_file = FileField

    # ステータス
    is_published = BooleanField  # 公開フラグ
```

### 2.3 既存モデル拡張
Projectモデルに追加:
```python
def get_progress_rate(self):
    """現在の進捗率を取得"""

def get_schedule_variance(self):
    """スケジュール差異を計算（予定-実績）"""

def is_delayed(self):
    """遅延しているか判定"""

def get_latest_progress(self):
    """最新の進捗記録を取得"""
```

## 3. ビジネスロジック

### 3.1 進捗計算（progress_utils.py）
```python
def calculate_project_progress(project):
    """プロジェクト進捗率を計算"""
    # ステータスベースの進捗率
    # ネタ: 10%, 施工日待ち: 30%, 進行中: 60%, 完工: 100%

def get_schedule_status(project):
    """スケジュール状況を判定"""
    # on_time, at_risk, delayed

def calculate_timeline_metrics(project):
    """タイムライン指標を計算"""
    # 予定日数、実績日数、残り日数

def get_delayed_projects():
    """遅延プロジェクト一覧を取得"""
```

### 3.2 レポート生成（report_utils.py）
```python
def generate_monthly_report(year, month):
    """月次経営レポートを生成"""
    # 売上・利益サマリー
    # プロジェクト進捗状況
    # キャッシュフロー状況
    # 予実対比

def generate_project_report(project_id):
    """プロジェクト別レポートを生成"""
    # プロジェクト詳細
    # 原価・利益分析
    # 進捗状況
    # 課題・リスク

def generate_cashflow_report(year, month):
    """キャッシュフローレポートを生成"""
    # 入出金予定
    # 売掛金・買掛金一覧
    # 資金繰り表

def generate_forecast_report(scenario_id):
    """予測レポートを生成"""
    # シナリオ詳細
    # 予測グラフ
    # 前提条件
```

### 3.3 PDF生成（pdf_utils.py）
```python
def generate_pdf_report(report_data, report_type):
    """レポートデータからPDFを生成"""
    # ReportLabを使用
    # テンプレートベースのレイアウト
    # チャート画像埋め込み

def embed_chart_in_pdf(chart_data):
    """チャートをPDFに埋め込み"""
    # matplotlib or plotly でチャート生成
    # 画像として保存してPDFに埋め込み
```

## 4. UI/UX設計

### 4.1 進捗管理ダッシュボード
**URL**: `/orders/progress/`

**レイアウト**:
```
+--------------------------------------+
| 進捗管理ダッシュボード                  |
+--------------------------------------+
| 📊 全体サマリー                        |
| - 進行中: XX件                        |
| - 遅延: XX件                          |
| - 完了: XX件                          |
+--------------------------------------+
| 🚨 遅延アラート                        |
| [遅延プロジェクト一覧]                  |
+--------------------------------------+
| 📈 プロジェクト進捗                    |
| [ガントチャート表示]                    |
+--------------------------------------+
```

### 4.2 レポート生成画面
**URL**: `/orders/reports/generate/`

**レイアウト**:
```
+--------------------------------------+
| レポート生成                          |
+--------------------------------------+
| レポートタイプ選択:                    |
| ○ 月次経営レポート                    |
| ○ プロジェクト別レポート              |
| ○ キャッシュフローレポート            |
| ○ 予測レポート                        |
+--------------------------------------+
| 対象期間:                             |
| [開始日] ～ [終了日]                  |
+--------------------------------------+
| オプション:                           |
| □ グラフを含める                      |
| □ 詳細データを含める                  |
| □ PDFで出力                          |
+--------------------------------------+
| [プレビュー] [生成]                   |
+--------------------------------------+
```

### 4.3 レポート一覧
**URL**: `/orders/reports/`

**レイアウト**:
```
+--------------------------------------+
| レポート一覧                          |
+--------------------------------------+
| [新規作成]  [検索]                    |
+--------------------------------------+
| タイトル | タイプ | 生成日 | 操作     |
| -------- | ------ | ------ | -------- |
| 2025/10月次 | 月次 | 10/31 | [DL][削除]|
| ...                                   |
+--------------------------------------+
```

## 5. API設計

### 5.1 進捗管理API
```
GET /orders/api/progress/
→ 全体進捗サマリー

GET /orders/api/progress/project/{id}/
→ プロジェクト別進捗詳細

POST /orders/api/progress/project/{id}/update/
→ 進捗更新

GET /orders/api/progress/delayed/
→ 遅延プロジェクト一覧

GET /orders/api/progress/gantt/
→ ガントチャート用データ
```

### 5.2 レポート生成API
```
POST /orders/api/reports/generate/
→ レポート生成

GET /orders/api/reports/{id}/
→ レポート取得

GET /orders/api/reports/{id}/pdf/
→ PDF ダウンロード

DELETE /orders/api/reports/{id}/
→ レポート削除
```

## 6. 実装順序

### Task 1: 進捗モデル設計（0.5日）
- ProjectProgressモデル作成
- Reportモデル作成
- マイグレーション

### Task 2: レポート生成ロジック（2日）
- report_utils.py作成
- 4種類のレポート生成関数
- データ集計・整形

### Task 3: PDF出力機能（1.5日）
- pdf_utils.py作成
- ReportLab統合
- テンプレートデザイン
- チャート埋め込み

### Task 4: ダッシュボード統合（1日）
- ProgressDashboardView
- ReportListView
- ReportGenerateView
- テンプレート作成

### Task 5: テスト・デバッグ（1日）
- 統合テスト
- PDF出力テスト
- レポート品質確認

**合計見積: 6日**

## 7. 技術スタック

### PDF生成
- **ReportLab**: Pythonで高品質PDFを生成
- **matplotlib**: チャート画像生成
- **日本語フォント**: IPAフォント使用

### 進捗管理
- **フロントエンド**: Chart.js (ガントチャート)
- **バックエンド**: Django ORM

## 8. 成功基準

✅ 月次経営レポートをPDF出力できる
✅ プロジェクト進捗をガントチャートで可視化できる
✅ 遅延プロジェクトを自動検出できる
✅ 4種類のレポートを生成できる
✅ レポートをPDF形式でダウンロードできる
✅ 日本語フォントが正しく表示される
