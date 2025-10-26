# Phase 2: 売上予測・収支シミュレーション機能 - 設計ドキュメント

## 1. 機能概要

### 1.1 売上予測エンジン
**目的**: 過去データとパイプラインから将来売上を予測

**入力データ**:
- 過去の受注実績（Project: project_status='完工'）
- 現在のパイプライン（ネタ、施工日待ち）
- 季節性係数
- 成約率設定（ステータス別）

**出力データ**:
- 月次売上予測（最悪・通常・最良）
- 四半期売上予測
- 年間売上予測
- 信頼区間

### 1.2 収支シミュレーション
**目的**: 売上予測に基づいた損益・キャッシュフロー予測

**計算式**:
```
予測売上 = 確定売上 + パイプライン売上 × 成約率
予測原価 = 予測売上 × 原価率
予測固定費 = 月次固定費合計
予測変動費 = 過去平均 × 調整係数
予測営業利益 = 予測売上 - 予測原価 - 予測固定費 - 予測変動費
```

### 1.3 シナリオ比較
**目的**: 複数のシナリオを並べて比較

**シナリオタイプ**:
1. **最悪シナリオ**: 成約率 30%、原価率 85%
2. **通常シナリオ**: 成約率 60%、原価率 75%
3. **最良シナリオ**: 成約率 90%、原価率 65%
4. **カスタムシナリオ**: ユーザー設定

## 2. データモデル

### 2.1 ForecastScenario モデル（新規作成）
```python
class ForecastScenario(models.Model):
    """売上予測シナリオ"""
    name = CharField  # シナリオ名
    description = TextField  # 説明
    created_by = ForeignKey(User)  # 作成者
    created_at = DateTimeField

    # 成約率設定（ステータス別）
    conversion_rate_neta = DecimalField  # ネタ→完工の成約率
    conversion_rate_waiting = DecimalField  # 施工日待ち→完工の成約率

    # コスト設定
    cost_rate = DecimalField  # 原価率（%）
    fixed_cost_multiplier = DecimalField  # 固定費係数（1.0 = 現状維持）
    variable_cost_multiplier = DecimalField  # 変動費係数

    # 予測設定
    forecast_months = IntegerField  # 予測月数（1-24）
    seasonality_enabled = BooleanField  # 季節性考慮

    # 予測結果（JSON格納）
    forecast_results = JSONField  # 予測結果データ

    is_active = BooleanField  # アクティブフラグ
```

### 2.2 既存モデル拡張
Projectモデルに追加メソッド:
```python
def get_conversion_probability(self):
    """ステータス別の成約確率を返す"""

def get_expected_revenue(self, conversion_rate):
    """期待売上を計算（金額 × 成約率）"""
```

## 3. ビジネスロジック

### 3.1 過去実績分析（forecast_utils.py）
```python
def analyze_historical_performance(months=12):
    """過去N ヶ月の実績を分析"""
    # 月次売上推移
    # 平均受注額、標準偏差
    # 成約率（ステータス遷移）
    # 季節性係数

def calculate_seasonal_index(year, month):
    """季節性指数を計算（1.0 = 平均月）"""

def get_conversion_rate_by_status(status, months=12):
    """ステータス別の過去成約率を計算"""
```

### 3.2 予測計算（forecast_utils.py）
```python
def generate_revenue_forecast(scenario, months=12):
    """売上予測を生成"""
    # 確定売上（既存完工案件）
    # パイプライン売上（ネタ、施工日待ち × 成約率）
    # 季節性調整
    # 最悪・通常・最良の3パターン

def generate_profit_forecast(scenario, revenue_forecast):
    """損益予測を生成"""
    # 原価予測
    # 固定費予測
    # 変動費予測
    # 営業利益予測

def generate_cashflow_forecast(scenario, months=12):
    """キャッシュフロー予測を生成"""
    # 入金予測（売上 + 入金サイト考慮）
    # 出金予測（原価 + 支払サイト考慮）
    # 月次キャッシュフロー
```

### 3.3 シナリオ比較（forecast_utils.py）
```python
def compare_scenarios(scenario_ids):
    """複数シナリオを比較"""
    # 各シナリオの予測結果を取得
    # 差分計算
    # 比較チャート用データ生成
```

## 4. UI/UX設計

### 4.1 売上予測ダッシュボード
**URL**: `/orders/forecast/`

**レイアウト**:
```
+--------------------------------------+
| 売上予測ダッシュボード                  |
+--------------------------------------+
| [シナリオ選択]  [新規作成]  [比較]      |
+--------------------------------------+
| 📊 予測サマリー                        |
| - 今月予測: ¥XX,XXX,XXX               |
| - 今期予測: ¥XX,XXX,XXX               |
| - 年間予測: ¥XX,XXX,XXX               |
+--------------------------------------+
| 📈 月次予測グラフ                      |
| [折れ線グラフ: 最悪・通常・最良]         |
+--------------------------------------+
| 🎯 パイプライン分析                    |
| ネタ: XX件 (¥XX,XXX,XXX)             |
| 施工日待ち: XX件 (¥XX,XXX,XXX)        |
| 期待売上: ¥XX,XXX,XXX                |
+--------------------------------------+
```

### 4.2 シナリオエディター
**URL**: `/orders/forecast/scenario/create/`

**入力フォーム**:
- シナリオ名
- 成約率スライダー（ネタ: 0-100%、施工日待ち: 0-100%）
- 原価率スライダー（50-100%）
- 固定費係数（0.5-2.0）
- 予測期間選択（3ヶ月、6ヶ月、12ヶ月、24ヶ月）
- 季節性考慮（ON/OFF）

**リアルタイムプレビュー**:
- 予測グラフ即座更新
- 予測損益即座計算

### 4.3 シナリオ比較ビュー
**URL**: `/orders/forecast/compare/`

**レイアウト**:
```
+--------------------------------------------------+
| シナリオ比較                                       |
+--------------------------------------------------+
| [シナリオA] vs [シナリオB] vs [シナリオC]           |
+--------------------------------------------------+
| 📊 比較チャート                                   |
| [重ね合わせグラフ: 各シナリオの売上予測]             |
+--------------------------------------------------+
| 📋 比較表                                         |
| 項目        | A        | B        | C        | 差分 |
| 年間売上    | ¥XXX     | ¥XXX     | ¥XXX     | ±XX%|
| 年間利益    | ¥XXX     | ¥XXX     | ¥XXX     | ±XX%|
| 利益率      | XX%      | XX%      | XX%      | ±XX%|
+--------------------------------------------------+
```

## 5. API設計

### 5.1 予測データAPI
```
GET /orders/api/forecast/revenue/?scenario_id=X&months=12
→ 月次売上予測データ（JSON）

GET /orders/api/forecast/profit/?scenario_id=X&months=12
→ 月次損益予測データ（JSON）

GET /orders/api/forecast/cashflow/?scenario_id=X&months=12
→ 月次キャッシュフロー予測データ（JSON）

GET /orders/api/forecast/pipeline/
→ 現在のパイプライン分析データ（JSON）
```

### 5.2 シナリオAPI
```
POST /orders/api/forecast/scenario/
→ 新規シナリオ作成

PUT /orders/api/forecast/scenario/{id}/
→ シナリオ更新

GET /orders/api/forecast/scenario/{id}/calculate/
→ シナリオ再計算

POST /orders/api/forecast/compare/
→ 複数シナリオ比較データ生成
```

## 6. 実装順序

### Task 1: 予測モデル設計（0.5日）
- ForecastScenarioモデル作成
- マイグレーション

### Task 2: シミュレーションロジック実装（2日）
- forecast_utils.py作成
- 過去実績分析関数
- 予測計算関数
- シナリオ比較関数

### Task 3: 予測ビュー作成（1日）
- ForecastDashboardView
- ScenarioCreateView
- ScenarioCompareView

### Task 4: 予測UI実装（1.5日）
- forecast_dashboard.html
- scenario_form.html
- scenario_compare.html
- JavaScriptでインタラクティブ更新

### Task 5: シナリオ比較機能（1日）
- 複数シナリオ選択UI
- 比較チャート
- 差分計算

### Task 6: テスト・デバッグ（1日）
- 統合テスト
- 計算精度検証
- UI/UXテスト

**合計見積: 7日**

## 7. 成功基準

✅ 過去12ヶ月の実績から売上予測を自動生成できる
✅ パイプライン案件の期待売上を計算できる
✅ 3つのシナリオ（最悪・通常・最良）を比較できる
✅ カスタムシナリオを作成・保存できる
✅ 予測結果をグラフで可視化できる
✅ 月次・四半期・年間の予測を表示できる
