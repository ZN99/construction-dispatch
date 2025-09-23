# 建築派遣SaaS - 軽量デモ版

このフォルダには、建築派遣SaaSシステムの軽量版デモが含まれています。

## 概要

このデモは、Django版の実装を基にした静的HTMLバージョンで、以下の機能を含んでいます：

### 主要機能
- **ダッシュボード** (`index.html`) - システム全体の概要とクイックアクション
- **案件管理** (`projects/`) - プロジェクトの作成、一覧表示、詳細表示
- **調査管理** (`surveys/`) - 調査のスケジューリング、実行、完了
- **職人管理** (`craftsman/`) - 職人の登録、配置、管理
- **資材業者管理** (`material/`) - 業者登録と管理
- **見積管理** (`pricing/`) - 見積作成と管理

### 特徴
- **ワークフロー進捗表示** - 案件登録から完了までの6段階の進捗表示
- **レスポンシブデザイン** - Bootstrap 5を使用したモダンなUI
- **日本語対応** - 完全日本語化されたインターフェース
- **ダミーデータ** - リアルなデータ例で機能を体験可能

## ファイル構成

```
demo_html/
├── index.html              # メインダッシュボード
├── css/
│   └── style.css          # カスタムスタイル
├── projects/              # 案件管理
│   ├── project_list.html  # 案件一覧
│   ├── project_detail.html # 案件詳細（ワークフロー表示付き）
│   └── project_create.html # 新規案件作成
├── surveys/               # 調査管理
│   ├── survey_list.html   # 調査一覧
│   ├── survey_detail.html # 調査詳細
│   ├── survey_create.html # 調査スケジュール
│   ├── survey_start.html  # 調査開始確認
│   ├── survey_complete.html # 調査完了
│   └── report_detail.html # 調査報告書
├── craftsman/             # 職人管理
│   ├── craftsman_list.html # 職人一覧
│   ├── craftsman_detail.html # 職人詳細
│   └── assignment_create.html # 職人配置
├── material/              # 資材業者
│   ├── supplier_list.html # 業者一覧
│   ├── supplier_detail.html # 業者詳細
│   └── supplier_create.html # 業者登録
└── pricing/               # 見積管理
    ├── pricing_list.html  # 見積一覧
    ├── pricing_detail.html # 見積詳細
    └── pricing_create.html # 見積作成
```

## 使用方法

1. `index.html`をブラウザで開く
2. サイドバーメニューまたはダッシュボードのリンクから各機能にアクセス
3. 全てのページが相互にリンクされており、実際のアプリケーションのような体験が可能

## 主要ワークフロー

1. **案件登録** → **調査スケジュール** → **調査実施** → **見積作成** → **職人配置** → **案件完了**

各段階で進捗が視覚的に表示され、現在のステータスが分かりやすく表示されます。

## 技術仕様

- HTML5 + CSS3 + JavaScript
- Bootstrap 5.1.3
- Font Awesome 6.0.0
- レスポンシブデザイン対応
- モダンブラウザ対応

## 注意事項

- これは静的HTMLデモ版です。データの保存や実際の処理は行われません
- 全ての機能はダミーデータとリンクで構成されています
- 本格的な実装はDjango版を参照してください