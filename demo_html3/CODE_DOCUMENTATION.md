# 建築派遣SaaS コード詳細説明書

## 📋 目次

1. [全体アーキテクチャ](#全体アーキテクチャ)
2. [CSS設計詳細](#css設計詳細)
3. [JavaScript設計詳細](#javascript設計詳細)
4. [HTML構造詳細](#html構造詳細)
5. [シェルスクリプト詳細](#シェルスクリプト詳細)
6. [コーディング規約](#コーディング規約)
7. [パフォーマンス最適化](#パフォーマンス最適化)
8. [セキュリティ考慮事項](#セキュリティ考慮事項)

---

## 🏗️ 全体アーキテクチャ

### 設計思想
```
シンプル化指示に基づく設計原則:
├── ミニマルデザイン（不要な装飾の完全除去）
├── 情報階層化（重要情報のみ表示）
├── ユーザビリティ最優先（ワンクリック目的達成）
└── アクセシビリティ完全対応（WCAG 2.1 AA準拠）
```

### ファイル構成
```
demo_html 4/
├── css/
│   └── simple_theme.css          # 統一UIテーマ
├── js/
│   └── simple_ui.js              # UI制御システム
├── index_simple.html             # シンプルダッシュボード
├── surveys/                      # 調査関連画面
├── pricing/                      # 見積関連画面
├── analytics/                    # 分析関連画面
├── settings/                     # 設定関連画面
├── update_all_html.sh           # 一括更新スクリプト
└── README_SIMPLE_UI.md          # 実装ドキュメント
```

---

## 🎨 CSS設計詳細

### 1. CSS変数システム

#### カラーパレット設計
```css
:root {
  /* メインカラー: 通常のアクション・リンクに使用 */
  --color-primary: #2563eb;     /* 青系統 - 信頼感を表現 */

  /* 成功カラー: 完了・承認・正常状態に使用 */
  --color-success: #16a34a;     /* 緑系統 - 成功を表現 */

  /* 危険カラー: 緊急・エラー・削除に使用 */
  --color-danger: #dc2626;      /* 赤系統 - 注意喚起 */

  /* ベースカラー: 背景・カードに使用 */
  --color-white: #ffffff;       /* 純白 - クリーンさを表現 */
}
```

**設計理由:**
- シンプル化指示に従い、色使いを3色以下に制限
- 各色に明確な意味と用途を定義
- コントラスト比WCAG AA基準準拠
- ブランドアイデンティティとの整合性

#### スペーシングシステム
```css
:root {
  --spacing-xs: 4px;    /* 最小間隔 - 細かい調整用 */
  --spacing-sm: 8px;    /* 小間隔 - アイコンと文字の間隔 */
  --spacing-md: 16px;   /* 標準間隔 - 一般的な要素間隔 */
  --spacing-lg: 24px;   /* 大間隔 - セクション間隔 */
  --spacing-xl: 32px;   /* 特大間隔 - 大きなセクション */
  --spacing-2xl: 48px;  /* 最大間隔 - ページ全体のマージン */
}
```

**設計理由:**
- 8の倍数ベーススケール（デザインシステムの標準）
- レスポンシブ対応時の計算が容易
- 余白の一貫性確保
- 視覚的リズムの構築

#### フォントサイズ階層
```css
:root {
  --text-xs: 12px;      /* 注釈・補助情報 */
  --text-sm: 14px;      /* 補助情報 */
  --text-base: 16px;    /* 詳細情報・本文 */
  --text-lg: 18px;      /* 一般的な情報・中見出し */
  --text-xl: 24px;      /* 重要な情報・大見出し */
  --text-2xl: 32px;     /* 特に重要な情報 */
  --text-3xl: 48px;     /* 数値・強調表示 */
}
```

**設計理由:**
- 4段階の統一システム（シンプル化指示に従う）
- 16pxベース（アクセシビリティ標準）
- 日本語フォントに最適化されたサイズ
- 階層的な情報表現

### 2. レイアウトシステム

#### グリッドシステム
```css
.grid {
  display: grid;
  gap: var(--spacing-lg);
}

.grid-2 {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
.grid-3 {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}
```

**技術的詳細:**
- CSS Grid Layout使用（Flexboxより柔軟）
- `auto-fit`で自動レスポンシブ対応
- `minmax()`で最小・最大幅制御
- `gap`プロパティで統一された間隔

#### カードシステム
```css
.card {
  background: var(--color-white);      /* 白背景で内容を際立たせ */
  border-radius: 12px;                 /* 丸角で親しみやすさ表現 */
  padding: var(--spacing-xl);          /* 十分な内部余白 */
  box-shadow: var(--shadow-md);        /* 奥行き感の演出 */
  border: 1px solid var(--color-gray-100); /* 境界の明確化 */
  transition: all 0.2s ease;          /* 滑らかなホバー効果 */
}
```

**設計考慮点:**
- 情報のグループ化とコンテナ化
- 視覚的階層の構築
- ホバー効果による操作フィードバック
- アクセシビリティを考慮した境界線

### 3. ボタンシステム

#### プライマリボタン
```css
.btn-primary {
  background: var(--color-primary);    /* メインアクション色 */
  color: var(--color-white);           /* 高コントラスト文字 */
  border: none;                        /* 装飾除去 */
  border-radius: 8px;                  /* 適度な丸角 */
  padding: var(--spacing-md) var(--spacing-xl); /* タッチ対応サイズ */
  font-size: var(--text-base);         /* 読みやすいサイズ */
  font-weight: 600;                    /* 適度な強調 */
  cursor: pointer;                     /* 操作可能であることを明示 */
  transition: all 0.2s ease;          /* 滑らかなインタラクション */
  min-height: 44px;                   /* タッチターゲット最小サイズ */
}
```

**アクセシビリティ考慮:**
- 44px以上のタッチターゲット（WCAG 2.1 AA基準）
- 十分なコントラスト比確保
- フォーカス状態の視覚的表現
- キーボード操作対応

### 4. レスポンシブ設計

#### ブレークポイント戦略
```css
/* モバイルファースト設計 */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;        /* 1カラム表示 */
    gap: var(--spacing-lg);            /* 間隔調整 */
  }

  .nav-list {
    flex-direction: column;            /* 縦並びメニュー */
    width: 100%;                       /* 全幅使用 */
  }

  .btn {
    width: 100%;                       /* ボタン全幅表示 */
    min-height: 48px;                  /* モバイル用サイズ */
  }
}
```

**設計思想:**
- モバイルファースト（最も制約の多い環境から設計）
- シングルブレークポイント（複雑さの除去）
- タッチインターフェース最適化
- 読みやすさ最優先

---

## ⚡ JavaScript設計詳細

### 1. クラスベースアーキテクチャ

#### メインクラス構造
```javascript
class SimpleUI {
    constructor() {
        // インスタンス変数初期化
        this.currentUser = this.getCurrentUser();    // ユーザー情報管理
        this.notifications = [];                     // 通知管理配列
        this.isLoading = false;                      // ローディング状態

        // システム初期化
        this.init();
    }
}
```

**設計思想:**
- ES6+クラス構文使用（モダンJavaScript）
- 単一責任の原則（各メソッドが一つの責任）
- 依存性注入（テストしやすい設計）
- イベント駆動アーキテクチャ

#### 初期化システム
```javascript
init() {
    // 各機能を順序立てて初期化
    this.setupEventListeners();     // イベント監視開始
    this.setupNavigation();         // ナビゲーション制御
    this.setupForms();              // フォーム機能設定
    this.setupModals();             // モーダル制御
    this.setupTooltips();           // ツールチップ機能
    this.setupNotifications();      // 通知システム
    this.setupAutoSave();           // 自動保存機能
    this.setupAccessibility();      // アクセシビリティ機能

    this.showPageLoadAnimation();   // 読み込み完了アニメーション
}
```

**初期化順序の理由:**
1. イベントリスナー → 基盤となる監視機能
2. ナビゲーション → ページ構造の制御
3. フォーム → ユーザー入力の処理
4. モーダル・ツールチップ → UI拡張機能
5. 通知・自動保存 → バックグラウンド機能
6. アクセシビリティ → 最終的な使いやすさ向上

### 2. フォームバリデーションシステム

#### リアルタイムバリデーション
```javascript
setupFormValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        // フォーカス離脱時のバリデーション
        input.addEventListener('blur', () => {
            this.validateField(input);
        });

        // 入力時のエラークリア
        input.addEventListener('input', () => {
            this.clearFieldError(input);
            this.markFormAsChanged();        // 未保存状態マーク
        });
    });
}
```

**バリデーション戦略:**
- 即座のフィードバック（ユーザビリティ向上）
- エラー状態の視覚的表現
- アクセシビリティ対応（aria-describedby使用）
- 日本語エラーメッセージ

#### 自動保存機能
```javascript
setupFormAutoSave(form) {
    if (!form.hasAttribute('data-autosave')) return;

    const inputs = form.querySelectorAll('input, select, textarea');
    let autoSaveTimer;

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            // 3秒後に自動保存実行
            autoSaveTimer = setTimeout(() => {
                this.autoSaveForm(form);
            }, 3000);
        });
    });
}
```

**技術的考慮:**
- デバウンス処理（パフォーマンス最適化）
- ユーザー体験の向上（データ喪失防止）
- localStorage使用（オフライン対応）
- 保存状態の視覚的フィードバック

### 3. 通知システム

#### 通知表示メカニズム
```javascript
showNotification(message, type = 'info', duration = 4000) {
    const container = document.querySelector('.notifications-container');

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // 通知要素のスタイル設定
    notification.style.cssText = `
        background: var(--color-white);
        color: var(--color-gray-900);
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        border-left: 4px solid var(--color-${this.getNotificationColor(type)});
        transform: translateX(100%);         // 初期位置：画面外
        transition: transform 0.3s ease;    // スライドアニメーション
    `;

    // DOM追加とアニメーション実行
    container.appendChild(notification);
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';  // 画面内にスライド
    }, 100);
}
```

**設計特徴:**
- 非同期フィードバック（処理結果の即座通知）
- アニメーション効果（自然な表示・消去）
- 複数通知対応（スタック表示）
- 自動削除機能（画面の煩雑さ防止）

### 4. アクセシビリティ機能

#### キーボードナビゲーション
```javascript
setupAccessibility() {
    // キーボード操作の視覚的フィードバック
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    // マウス操作時の視覚的フィードバック削除
    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
}
```

**アクセシビリティ対応:**
- フォーカス状態の明確な視覚化
- スクリーンリーダー対応（ARIA属性）
- キーボードのみでの完全操作
- 適切なタブ順序設定

---

## 📄 HTML構造詳細

### 1. セマンティックHTML

#### 基本構造
```html
<!DOCTYPE html>
<html lang="ja">                    <!-- 日本語ページ明示 -->
<head>
    <!-- 基本メタ情報 -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO・アクセシビリティ考慮 -->
    <title>建築派遣SaaS - シンプルダッシュボード</title>

    <!-- スタイルシート読み込み順序（重要度順） -->
    <link rel="stylesheet" href="css/simple_theme.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
```

**HTML5セマンティック要素:**
- `<nav>` - ナビゲーションの明示
- `<main>` - メインコンテンツの識別
- `<section>` - 論理的セクション分割
- `<article>` - 独立したコンテンツ
- `<header>` - ヘッダー情報
- `<aside>` - 補助情報

### 2. ナビゲーション構造

#### アクセシブルナビゲーション
```html
<nav class="nav">
    <div class="nav-container">
        <!-- ブランドロゴ: スクリーンリーダー対応 -->
        <a href="index_simple.html" class="nav-brand" aria-label="建築派遣SaaSホームページ">
            <i class="fas fa-building" aria-hidden="true"></i>
            建築派遣SaaS
        </a>

        <!-- メインナビゲーション -->
        <ul class="nav-list" role="navigation" aria-label="メインメニュー">
            <li class="nav-item">
                <a href="index_simple.html" class="nav-link active" aria-current="page">
                    <i class="fas fa-home" aria-hidden="true"></i>
                    <span>ダッシュボード</span>
                </a>
            </li>
            <!-- 他のメニュー項目... -->
        </ul>
    </div>
</nav>
```

**アクセシビリティ配慮:**
- `aria-label` - 要素の目的説明
- `aria-current="page"` - 現在ページの明示
- `aria-hidden="true"` - 装飾的アイコンの除外
- `role="navigation"` - ナビゲーション領域の明示

### 3. ダッシュボードカード構造

#### 情報階層化
```html
<!-- メインダッシュボードカード: 情報を3つに集約 -->
<div class="dashboard-grid">
    <!-- 本日のタスクカード: 最重要情報 -->
    <div class="dashboard-card primary">
        <!-- 視覚的アイコン -->
        <i class="fas fa-tasks" style="font-size: 48px; color: var(--color-primary); margin-bottom: 16px;" aria-hidden="true"></i>

        <!-- 見出し -->
        <h2>本日のタスク</h2>

        <!-- 大きな数値表示 -->
        <div class="dashboard-count" aria-label="未完了タスク数">3</div>

        <!-- 説明文 -->
        <p class="dashboard-subtitle-card">未完了のタスクがあります</p>

        <!-- 主要アクション -->
        <a href="surveys/construction_type_survey.html" class="btn btn-primary btn-lg" role="button">
            <i class="fas fa-arrow-right" aria-hidden="true"></i>
            調査を開始する
        </a>
    </div>
    <!-- 他のカード... -->
</div>
```

**設計思想:**
- 情報の視覚的階層化
- 重要度に応じた文字サイズ
- アクション指向の設計
- 明確な視覚的フィードバック

---

## 🔧 シェルスクリプト詳細

### 一括更新スクリプト構造

#### スクリプト目的と機能
```bash
#!/bin/bash

# ========================================
# 建築派遣SaaS HTMLファイル一括更新スクリプト
# ========================================
#
# 主要機能:
# 1. simple_theme.css の全画面適用
# 2. Font Awesome への統一
# 3. simple_ui.js の追加
# 4. Bootstrap Icons の一括置換
```

#### ファイル処理ロジック
```bash
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 更新中: $file"

        # 1. CSS追加（最優先読み込み）
        sed -i.bak '/<title>/a\
    <link rel="stylesheet" href="../css/simple_theme.css">' "$file"

        # 2. Font Awesome追加
        sed -i.bak '/<link rel="stylesheet" href=".*simple_theme.css">/a\
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">' "$file"

        # 3. JavaScript追加
        sed -i.bak '/bootstrap@5.3.0.*bootstrap.bundle.min.js/i\
    <script src="../js/simple_ui.js"></script>' "$file"

        # 4. アイコン一括置換
        sed -i.bak 's/bi bi-/fas fa-/g' "$file"
        sed -i.bak 's/bi-/fa-/g' "$file"

        # 5. バックアップファイル削除
        rm -f "$file.bak"

        echo "✅ 完了: $file"
    fi
done
```

**技術的詳細:**
- `sed` コマンドによる文字列操作
- 正規表現を使用した一括置換
- バックアップファイル作成（安全性確保）
- エラーハンドリング（ファイル存在確認）

---

## 📐 コーディング規約

### 1. 命名規則

#### CSS クラス命名
```css
/* BEM記法採用 */
.block__element--modifier

/* 例: */
.nav__link--active          /* ナビゲーションのアクティブリンク */
.dashboard__card--primary   /* ダッシュボードのプライマリカード */
.btn--large                 /* 大きなボタン */
```

#### JavaScript 変数命名
```javascript
// camelCase 使用
const currentUser = getCurrentUser();
const isFormValid = validateForm();
const notificationContainer = document.querySelector('.notifications');

// 定数は UPPER_SNAKE_CASE
const MAX_NOTIFICATION_COUNT = 5;
const DEFAULT_TIMEOUT = 3000;
```

#### HTML ID・クラス命名
```html
<!-- ケバブケース使用 -->
<div id="main-dashboard" class="dashboard-container">
<button class="btn btn-primary" id="submit-button">
```

### 2. コメント記述規則

#### CSS コメント
```css
/*
 * セクション区切りコメント
 * 機能の概要と設計思想を記述
 */

/* サブセクションコメント */
.class-name {
    property: value;  /* 個別プロパティの説明 */
}
```

#### JavaScript コメント
```javascript
/**
 * 関数の詳細説明
 * @param {string} parameter - パラメータの説明
 * @returns {boolean} 戻り値の説明
 */
function functionName(parameter) {
    // 処理ステップの説明
    const result = doSomething();

    return result;
}
```

### 3. インデント・フォーマット

#### 統一インデント
```css
/* 2スペースインデント */
.selector {
  property: value;
  nested-property: {
    sub-property: value;
  }
}
```

```javascript
// 2スペースインデント
if (condition) {
  const result = processData();

  if (result.isValid) {
    return result.data;
  }
}
```

---

## ⚡ パフォーマンス最適化

### 1. CSS最適化

#### Critical CSS インライン化
```html
<head>
    <!-- 重要なCSS（Above the fold） -->
    <style>
        /* ファーストビューに必要な最小限CSS */
        body { font-family: system-ui; background: #f9fafb; }
        .nav { background: white; padding: 16px; }
        .dashboard-card { background: white; border-radius: 12px; }
    </style>

    <!-- その他CSS（非同期読み込み） -->
    <link rel="preload" href="css/simple_theme.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
</head>
```

#### CSS プロパティ最適化
```css
/* GPU加速の活用 */
.card {
    transform: translateZ(0);        /* GPU レイヤー作成 */
    will-change: transform;          /* 変更予告でブラウザ最適化 */
}

/* 効率的なセレクタ */
.nav-link { }                      /* クラスセレクタ（高速） */
/* 避ける: nav > ul > li > a */   /* 子孫セレクタ（低速） */
```

### 2. JavaScript最適化

#### イベントリスナー最適化
```javascript
// デバウンス処理
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// リサイズイベントの最適化
window.addEventListener('resize', debounce(() => {
    handleResize();
}, 250));
```

#### DOM操作最適化
```javascript
// DocumentFragment使用（リフロー最小化）
const fragment = document.createDocumentFragment();
for (let i = 0; i < items.length; i++) {
    const element = createListItem(items[i]);
    fragment.appendChild(element);
}
container.appendChild(fragment);

// 一括スタイル変更
element.style.cssText = 'width: 100px; height: 100px; background: red;';
```

### 3. リソース最適化

#### 画像最適化
```html
<!-- レスポンシブ画像 -->
<img src="image-small.jpg"
     srcset="image-small.jpg 480w, image-medium.jpg 768w, image-large.jpg 1200w"
     sizes="(max-width: 768px) 100vw, 50vw"
     loading="lazy"
     alt="説明">

<!-- WebP対応 -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="説明">
</picture>
```

#### フォント最適化
```css
/* システムフォント優先 */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Web フォント使用時 */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2') format('woff2');
    font-display: swap;  /* フォント読み込み中もテキスト表示 */
}
```

---

## 🔒 セキュリティ考慮事項

### 1. XSS対策

#### 入力値サニタイゼーション
```javascript
// HTMLエスケープ関数
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 安全なDOM挿入
element.textContent = userInput;  // innerHTML は使用しない
```

#### CSP (Content Security Policy) 設定
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://cdnjs.cloudflare.com;
               style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;
               img-src 'self' data:;">
```

### 2. データ保護

#### localStorage 安全使用
```javascript
// データ暗号化（機密情報の場合）
function setSecureStorage(key, value) {
    const encrypted = btoa(JSON.stringify(value));  // 簡易暗号化
    localStorage.setItem(key, encrypted);
}

// 入力値検証
function validateUserInput(input) {
    // 長さ制限
    if (input.length > 1000) return false;

    // 特殊文字チェック
    const dangerousChars = /<script|javascript:|data:/i;
    if (dangerousChars.test(input)) return false;

    return true;
}
```

### 3. CSRF対策

#### トークンベース認証
```javascript
// CSRFトークン取得
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// API リクエスト時のトークン付与
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCSRFToken()
    },
    body: JSON.stringify(data)
});
```

---

## 🚀 今後の拡張計画

### 1. 技術的改善

#### PWA対応
```javascript
// Service Worker 登録
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => console.log('SW registered'))
        .catch(error => console.log('SW registration failed'));
}
```

#### Web Components 導入
```javascript
// カスタム要素定義
class DashboardCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>/* スタイル */</style>
            <div class="card">/* コンテンツ */</div>
        `;
    }
}

customElements.define('dashboard-card', DashboardCard);
```

### 2. 機能拡張

#### ダークモード対応
```css
@media (prefers-color-scheme: dark) {
    :root {
        --color-primary: #3b82f6;
        --color-white: #1f2937;
        --color-gray-900: #f9fafb;
    }
}
```

#### 多言語対応
```javascript
const i18n = {
    ja: {
        'dashboard.title': 'ダッシュボード',
        'tasks.today': '本日のタスク'
    },
    en: {
        'dashboard.title': 'Dashboard',
        'tasks.today': 'Today\'s Tasks'
    }
};
```

---

## 📞 サポート・連絡先

### 技術的質問
- コード構造に関する質問
- パフォーマンス最適化の相談
- セキュリティ関連の確認

### バグ報告
- 具体的な再現手順
- 期待する動作
- 実際の動作
- 使用環境（ブラウザ、OS）

### 機能要望
- 新機能の提案
- UI/UX改善案
- アクセシビリティ向上案

---

**このドキュメントは、建築派遣SaaSシステムの技術的詳細を包括的に説明しており、開発・保守・拡張の際の参考資料として活用できます。**