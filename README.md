# 建築派遣管理システム (Construction Dispatch Management System)

Django + Pythonで構築した建築業界向けの総合管理システムです。原状回復・クリーニング・クロス貼り替えなどの建築工事を効率的に管理し、現場調査から業者発注、支払い管理まで一元化できるWebアプリケーションです。

## 🚀 本番環境

**URL**: https://construction-dispatch.onrender.com/

## 🔐 デモ用アカウント

### 管理者アカウント
- **Username**: `admin`
- **Password**: (設定済み)
- **アクセス**: 全機能利用可能

### 本部管理者
- **Username**: `headquarters`
- **Password**: `password123`
- **アクセス**: 管理ダッシュボード、統合ダッシュボード

### 調査員アカウント（8名）
| Username | 氏名 | Email | パスワード |
|----------|------|-------|-----------|
| `tanaka` | 田中 太郎 | tanaka@company.com | password123 |
| `sato` | 佐藤 花子 | sato@company.com | password123 |
| `S003` | 山田 次郎 | yamada@company.com | password123 |
| `S004` | 鈴木 美穂 | suzuki@company.com | password123 |
| `tanaka2` | 田中 太郎 | tanaka@example.com | password123 |
| `taniguchi_m` | 谷口 美咲 | taniguchi@company.com | password123 |
| `ito_h` | 伊藤 博志 | ito@company.com | password123 |
| `watanabe_k` | 渡辺 健太 | watanabe@company.com | password123 |

## 🏢 サンプル業者データ（15社）

### 原状回復・クリーニング専門業者
- **クリーニング専門ABC** - ハウスクリーニング、オフィスクリーニング
- **原状回復のプロ** - 賃貸物件原状回復、クロス貼り替え
- **リフォーム工房みどり** - 内装工事、クロス貼り替え、床張り替え
- **クリーンサービス東京** - エアコンクリーニング、水回りクリーニング
- **住宅メンテナンス川崎** - 住宅原状回復、設備メンテナンス
- **プロクリーナーズ** - 店舗クリーニング、オフィス清掃
- **リペア・スペシャリスト** - 壁紙補修、フローリング補修

## 📊 主要機能

### 🎯 統合ダッシュボード
- **V字回復成長ストーリー**: 2023年苦境から2024年9月の絶好調まで
- **現実的なKPI**: 月間売上¥5,234,000、純利益¥895,000、利益率17.1%
- **業績推移**: 過去18ヶ月のトレンド分析
- **年間業績サマリー**: 折りたたみ式詳細テーブル
- **財務詳細ビュー** / **運用詳細ビュー**の切り替え

### 🏗️ 案件管理
- **案件一覧・検索**: ステータス別フィルタリング
- **新規案件登録**: 原状回復、クリーニング、クロス貼り替え対応
- **進捗管理**: 受注〜完了までのステータス追跡
- **収益性分析**: プロジェクト別利益率計算

### 🔍 現場調査
- **調査スケジュール管理**: カレンダー表示
- **調査員アサイン**: 8名の調査員による効率的な配置
- **ルート最適化**: Google Maps連携（要API設定）
- **調査結果記録**: 写真・メモ・測定データ

### 🤝 業者管理
- **業者マスター**: 15社の専門業者データ
- **発注管理**: 業者別の発注履歴・実績
- **業者ダッシュボード**: パフォーマンス分析
- **支払い管理**: 入金・出金追跡

### 💰 経理・支払
- **入金管理**: 顧客からの入金記録
- **出金管理**: 業者への支払い記録
- **利益分析**: 案件別・月別利益計算
- **キャッシュフロー**: 7ヶ月連続黒字達成

## 🛠️ 技術構成

- **バックエンド**: Django 5.2.6 + Python 3.11
- **データベース**: SQLite（開発・本番）
- **フロントエンド**: Bootstrap 5.1.3 + jQuery + Chart.js
- **デプロイ**: Render Platform
- **画像管理**: Pillow 11.3.0
- **HTTP**: Requests 2.32.5
- **日付処理**: python-dateutil 2.9.0

## 📦 セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/ZN99/construction-dispatch.git
cd construction-dispatch
```

### 2. 仮想環境作成・有効化
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 4. データベース初期化
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 管理者ユーザー作成
```bash
python manage.py createsuperuser
```

### 6. 開発サーバー起動
```bash
python manage.py runserver
```

## 🌐 主要URL

| URL | 機能 | 説明 |
|-----|------|------|
| `/` | 統合ダッシュボード | V字回復ストーリー表示 |
| `/orders/login/` | ログイン | 本部・調査員共通 |
| `/orders/dashboard/` | 管理ダッシュボード | 従来のシンプル版 |
| `/orders/ultimate-dashboard/` | 統合ダッシュボード | 新UI・高機能版 |
| `/orders/projects/` | 案件管理 | 案件一覧・作成・編集 |
| `/surveys/schedule/` | 調査管理 | スケジュール・アサイン |
| `/orders/contractor-dashboard/` | 業者管理 | 受注業者一覧 |
| `/orders/ordering-dashboard/` | 発注管理 | 発注業者一覧 |
| `/admin/` | Django管理画面 | システム管理 |

## 📋 主要モデル

### User (ユーザー)
- Django標準User + 調査員プロファイル連携

### Project (案件)
- site_name, site_address, contractor_name, status, work_dates, amount

### Surveyor (調査員)
- name, employee_id, email, phone, department, user, specialties

### Survey (調査)
- project, surveyor, scheduled_date, status, results

### Contractor (業者)
- name, address, contact_person, phone, email, specialties, hourly_rate

## 🎨 UI/UX特徴

### 🌟 統合ダッシュボード
- **グラスモーフィズムデザイン**: モダンで洗練された外観
- **レスポンシブ対応**: タブレット・スマホ対応
- **インタラクティブチャート**: Chart.js使用
- **アニメーション**: CSS transitions + JavaScript

### 📱 モバイル対応
- Bootstrap 5の完全レスポンシブ
- タッチフレンドリーなボタンサイズ
- 現場での使いやすさを重視

### 🎯 ユーザビリティ
- 直感的なナビゲーション
- ステータスの色分け表示
- 検索・フィルタ機能充実

## 🔧 カスタマイズ設定

### Google Maps API (現場調査ルート機能)
```python
# surveys/templates/surveys/survey_route_detail.html
# 183行目の YOUR_API_KEY を実際のAPIキーに置換
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=geometry,places"></script>
```

### デバッグモード
- **Ctrl + Shift + D**: 隠されたチャートを表示
- **localStorage**: 設定永続化

## 📈 実装済み機能

### ✅ 完了機能
- [x] 統合ダッシュボード（V字回復ストーリー）
- [x] 案件管理（CRUD操作）
- [x] 調査員管理（8名フル登録）
- [x] 業者管理（15社サンプルデータ）
- [x] 現場調査スケジュール
- [x] 経理・支払い管理
- [x] レスポンシブデザイン
- [x] 本番環境デプロイ

### 🚧 今後の拡張予定
- [ ] Google Maps API統合
- [ ] メール通知機能
- [ ] PDF帳票出力
- [ ] REST API提供
- [ ] モバイルアプリ化
- [ ] 多言語対応

## 🐛 デバッグ・トラブルシューティング

### テンプレートエラー
```bash
# base.htmlが見つからない場合
# settings.pyのTEMPLATES.DIRSを確認
TEMPLATES = [
    {
        "DIRS": [BASE_DIR / 'templates'],  # この行が必要
    }
]
```

### 静的ファイル
```bash
# 本番環境で静的ファイルが表示されない場合
python manage.py collectstatic
```

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエスト歓迎！バグ報告や機能提案はIssuesへお願いします。

---

**🏢 建築派遣管理システム** - 原状回復・クリーニング業界のDXを推進