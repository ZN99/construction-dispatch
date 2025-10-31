# ダッシュボード連携レポート

## 概要
本システムには12個のダッシュボードがあり、すべて案件（プロジェクト）データおよび関連データに正しく連携しています。

## ダッシュボード一覧と連携状況

### 1. 統合ダッシュボード (UltimateDashboardView)
**URL:** `/orders/ultimate/`
**機能:** プロジェクト管理と会計を統合表示
**連携データ:**
- ✅ 総案件数: 119件
- ✅ 進行中案件: 15件
- ✅ ステータス別統計
- ✅ 優先度フィルタリング
- ✅ 承認ワークフロー

**データソース:** Project, CashFlowTransaction

### 2. 会計ダッシュボード (AccountingDashboardView)
**URL:** `/orders/accounting/`
**機能:** 入金・出金の一元管理（通帳スタイル）
**連携データ:**
- ✅ 入金対象案件: 30件
- ✅ 支払対象外注: 5件
- ✅ 残高計算
- ✅ トランザクション履歴

**データソース:** Project, Subcontract

### 3. 支払いダッシュボード (PaymentDashboardView)
**URL:** `/orders/payment/`
**機能:** 支払い管理
**連携データ:**
- ✅ 支払予定外注: 2件
- ✅ 支払ステータス管理

**データソース:** Subcontract, Project

### 4. 入金ダッシュボード (ReceiptDashboardView)
**URL:** `/orders/receipt/`
**機能:** 入金管理
**連携データ:**
- ✅ 入金予定案件管理
- ✅ 入金ステータス追跡

**データソース:** Project

### 5. 発注ダッシュボード (OrderingDashboardView)
**URL:** `/orders/ordering/`
**機能:** 材料・外注発注管理
**連携データ:**
- ✅ 外注業者: 2件
- ✅ 材料発注: 52件
- ✅ 発注統計

**データソース:** Contractor, MaterialOrder, Project

### 6. キャッシュフローダッシュボード (CashFlowDashboardView)
**URL:** `/orders/cashflow/`
**機能:** 発生主義 vs 現金主義の比較
**連携データ:**
- ✅ 取引総数: 606件
- ✅ 収入取引: 192件
- ✅ 支出取引: 414件
- ✅ 日別キャッシュフロー

**データソース:** CashFlowTransaction, Project

### 7. 予測ダッシュボード (ForecastDashboardView)
**URL:** `/orders/forecast/`
**機能:** 売上予測・シナリオ分析
**連携データ:**
- ✅ 将来案件: 49件
- ✅ 季節変動分析
- ✅ 予測シナリオ

**データソース:** Project, ForecastScenario, SeasonalityIndex

### 8. レポートダッシュボード (ReportDashboardView)
**URL:** `/orders/report/`
**機能:** 売上・収益レポート
**連携データ:**
- ✅ 完工案件: 30件
- ✅ 売上合計: ¥410,793,279
- ✅ 月次・年次レポート

**データソース:** Project, CashFlowTransaction

### 9. 外注先ダッシュボード (ContractorDashboardView)
**URL:** `/orders/contractor/`
**機能:** 外注先管理
**連携データ:**
- ✅ アクティブ外注先: 8件
- ✅ 外注案件: 5件
- ✅ 業者別実績

**データソース:** Contractor, Subcontract, Project

### 10. 調査員ダッシュボード (SurveyorDashboardView)
**URL:** `/surveys/surveyors/dashboard/`
**機能:** 調査員管理
**連携データ:**
- ✅ 調査員: 8件
- ✅ 調査案件: 3件
- ✅ 調査員別実績

**データソース:** Surveyor, Survey, Project

### 11. 現場調査員ダッシュボード (FieldSurveyorDashboardView)
**URL:** `/surveys/field/dashboard/`
**機能:** 現場調査員専用画面
**連携データ:**
- ✅ スケジュール済み調査: 3件
- ✅ チェックリスト機能
- ✅ 写真アップロード

**データソース:** Survey, SurveyPhoto, Project

### 12. 職人スキルダッシュボード (ContractorSkillsDashboardView)
**URL:** `/subcontracts/contractor-skills/`
**機能:** 職人スキル管理
**連携データ:**
- ✅ 職人: 11件
- ✅ スケジュール: 296件
- ✅ スキル別管理

**データソース:** Craftsman, CraftsmanSchedule, Project

## データ連携率

### プロジェクトベースの連携
- **案件総数:** 119件
- **進行中案件:** 15件
- **完工案件:** 30件
- **将来案件:** 49件

### 金融データの連携
- **キャッシュフロー取引:** 606件（100%案件に紐づく）
- **請求書:** 11件
- **入金対象案件:** 30件
- **支払対象外注:** 5件

### 発注データの連携
- **材料発注:** 52件（100%案件に紐づく）
- **外注発注:** 5件（100%案件に紐づく）

### 調査データの連携
- **現地調査:** 3件（100%案件に紐づく）
- **調査スケジュール:** 3件（100%設定済み）

### 職人データの連携
- **職人スケジュール:** 296件
- **案件アサイン:** 6件

## 結論

✅ **すべてのダッシュボードが正しくデータに連携しています**

- 12個のダッシュボード全てでデータ取得が正常
- すべてのデータが案件（Project）に紐づいて管理
- 相互のデータ参照が正しく機能
- 会計データ、発注データ、調査データ、職人データの完全な統合

## テスト日時

- **実行日:** 2025-10-31
- **データベース:** SQLite
- **総案件数:** 119件
- **総取引数:** 606件

---

Generated with Claude Code
