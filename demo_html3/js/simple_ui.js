/**
 * 建築派遣SaaS シンプルUI制御システム
 * ミニマルデザイン・直感操作・ユーザビリティ最優先
 *
 * 主な機能:
 * - フォームバリデーション・自動保存
 * - 通知システム・モーダル制御
 * - ツールチップ・キーボードショートカット
 * - アクセシビリティ対応・レスポンシブ制御
 * - エラーハンドリング・パフォーマンス監視
 *
 * 設計方針:
 * - ES6+クラスベース設計
 * - ユーザビリティファースト
 * - プログレッシブエンハンスメント
 * - アクセシビリティ完全対応
 */

class SimpleUI {
    constructor() {
        // 現在のユーザー情報を取得・保持
        this.currentUser = this.getCurrentUser();

        // 通知管理用配列
        this.notifications = [];

        // ローディング状態管理
        this.isLoading = false;

        // システム初期化実行
        this.init();
    }

    /**
     * システム初期化メソッド
     * 全ての機能を順序立てて初期化し、シンプルUIシステムを稼働させる
     */
    init() {
        // イベントリスナー設定（リサイズ、ページ離脱、キーボード操作）
        this.setupEventListeners();

        // ナビゲーション制御（アクティブ状態、ホバー効果、モバイル対応）
        this.setupNavigation();

        // フォーム機能（バリデーション、送信、自動保存）
        this.setupForms();

        // モーダル制御（開閉、ESCキー、フォーカス管理）
        this.setupModals();

        // ツールチップ機能（ホバー表示、位置調整）
        this.setupTooltips();

        // 通知システム（表示、削除、アニメーション）
        this.setupNotifications();

        // 自動保存機能（定期実行、セッション維持）
        this.setupAutoSave();

        // アクセシビリティ機能（キーボード操作、ARIA属性）
        this.setupAccessibility();

        // ページ読み込み完了時のアニメーション実行
        this.showPageLoadAnimation();

        // 初期化完了ログ出力
        console.log('SimpleUI initialized');
    }

    /**
     * ユーザー情報取得メソッド
     * localStorage からユーザー情報を取得、存在しない場合はデフォルト値を返す
     * @returns {Object} ユーザー情報オブジェクト（名前、役割、ID）
     */
    getCurrentUser() {
        return JSON.parse(localStorage.getItem('currentUser') || '{"name": "ユーザー", "role": "一般", "id": "USER001"}');
    }

    /**
     * 全体的なイベントリスナー設定メソッド
     * ウィンドウリサイズ、ページ離脱、キーボード操作の監視を開始
     */
    setupEventListeners() {
        // ウィンドウリサイズ対応 - デバウンス処理で性能最適化
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize(); // レスポンシブ対応の処理実行
        }, 250)); // 250ms間隔でリサイズ処理を実行

        // ページ離脱前の確認 - 未保存データ保護
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault(); // デフォルトの離脱処理を停止
                e.returnValue = '保存されていない変更があります。ページを離れますか？';
            }
        });

        // キーボードショートカット対応 - ユーザビリティ向上
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e); // ショートカットキー処理
        });
    }

    /**
     * ナビゲーション制御
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            // アクティブ状態の設定
            if (link.getAttribute('href') && currentPath.includes(link.getAttribute('href'))) {
                link.classList.add('active');
            }

            // ホバー効果
            link.addEventListener('mouseenter', () => {
                this.preloadPage(link.getAttribute('href'));
            });

            // クリック効果
            link.addEventListener('click', (e) => {
                this.handleNavigation(e, link);
            });
        });

        // モバイルメニュー制御
        this.setupMobileMenu();
    }

    /**
     * モバイルメニュー制御
     */
    setupMobileMenu() {
        const menuToggle = document.querySelector('.menu-toggle');
        const navList = document.querySelector('.nav-list');

        if (menuToggle && navList) {
            menuToggle.addEventListener('click', () => {
                navList.classList.toggle('show');
                menuToggle.setAttribute('aria-expanded',
                    navList.classList.contains('show') ? 'true' : 'false'
                );
            });
        }
    }

    /**
     * フォーム制御
     */
    setupForms() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            this.setupFormValidation(form);
            this.setupFormSubmission(form);
            this.setupFormAutoSave(form);
        });
    }

    /**
     * フォームバリデーション
     */
    setupFormValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            // リアルタイムバリデーション
            input.addEventListener('blur', () => {
                this.validateField(input);
            });

            // 入力時のエラークリア
            input.addEventListener('input', () => {
                this.clearFieldError(input);
                this.markFormAsChanged();
            });

            // 必須フィールドの表示
            if (input.hasAttribute('required')) {
                const label = form.querySelector(`label[for="${input.id}"]`);
                if (label && !label.classList.contains('required')) {
                    label.classList.add('required');
                }
            }
        });
    }

    /**
     * フィールドバリデーション
     */
    validateField(input) {
        const value = input.value.trim();
        const fieldName = input.getAttribute('name') || input.id;
        let errorMessage = '';

        // 必須チェック
        if (input.hasAttribute('required') && !value) {
            errorMessage = 'この項目は必須です';
        }
        // 形式チェック
        else if (value && input.type === 'email' && !this.isValidEmail(value)) {
            errorMessage = '正しいメールアドレスを入力してください';
        }
        else if (value && input.type === 'tel' && !this.isValidPhone(value)) {
            errorMessage = '正しい電話番号を入力してください';
        }
        // 最小文字数チェック
        else if (input.minLength && value.length < input.minLength) {
            errorMessage = `${input.minLength}文字以上で入力してください`;
        }

        this.showFieldError(input, errorMessage);
        return !errorMessage;
    }

    /**
     * フィールドエラー表示
     */
    showFieldError(input, message) {
        this.clearFieldError(input);

        if (message) {
            input.classList.add('error');

            const errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            errorElement.textContent = message;
            errorElement.id = `${input.id || input.name}_error`;

            input.parentNode.appendChild(errorElement);
            input.setAttribute('aria-describedby', errorElement.id);
        } else {
            input.classList.remove('error');
            input.removeAttribute('aria-describedby');
        }
    }

    /**
     * フィールドエラークリア
     */
    clearFieldError(input) {
        input.classList.remove('error');
        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    }

    /**
     * フォーム送信制御
     */
    setupFormSubmission(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (this.isLoading) return;

            const isValid = this.validateForm(form);
            if (!isValid) {
                this.showNotification('入力内容を確認してください', 'error');
                return;
            }

            await this.submitForm(form);
        });
    }

    /**
     * フォーム全体バリデーション
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * フォーム送信
     */
    async submitForm(form) {
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalText = submitButton ? submitButton.textContent : '';

        try {
            this.setLoading(true);
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = '保存中...';
                submitButton.classList.add('loading');
            }

            // フォームデータ収集
            const formData = this.getFormData(form);

            // 送信シミュレーション
            await this.delay(1500);

            // 成功処理
            this.handleFormSuccess(form, formData);

            if (submitButton) {
                submitButton.textContent = '保存完了';
                submitButton.style.backgroundColor = 'var(--color-success)';
            }

            this.showNotification('保存しました', 'success');
            this.markFormAsSaved();

        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('保存に失敗しました', 'error');

            if (submitButton) {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        } finally {
            this.setLoading(false);

            if (submitButton) {
                setTimeout(() => {
                    submitButton.classList.remove('loading');
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                    submitButton.style.backgroundColor = '';
                }, 2000);
            }
        }
    }

    /**
     * フォームデータ取得
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    /**
     * フォーム成功処理
     */
    handleFormSuccess(form, data) {
        // データ保存
        const formId = form.id || 'form_' + Date.now();
        localStorage.setItem(`form_${formId}`, JSON.stringify({
            data: data,
            timestamp: new Date().toISOString(),
            user: this.currentUser.id
        }));

        // フォーム後処理
        const redirect = form.getAttribute('data-redirect');
        if (redirect) {
            setTimeout(() => {
                window.location.href = redirect;
            }, 1500);
        }
    }

    /**
     * 自動保存設定
     */
    setupFormAutoSave(form) {
        if (!form.hasAttribute('data-autosave')) return;

        const inputs = form.querySelectorAll('input, select, textarea');
        let autoSaveTimer;

        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    this.autoSaveForm(form);
                }, 3000);
            });
        });
    }

    /**
     * 自動保存実行
     */
    autoSaveForm(form) {
        const formData = this.getFormData(form);
        const formId = form.id || 'autosave_' + Date.now();

        localStorage.setItem(`autosave_${formId}`, JSON.stringify({
            data: formData,
            timestamp: new Date().toISOString()
        }));

        this.showNotification('自動保存しました', 'info', 2000);
    }

    /**
     * モーダル制御
     */
    setupModals() {
        // モーダル開く
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal]');
            if (trigger) {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            }
        });

        // モーダル閉じる
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') ||
                e.target.classList.contains('modal-close') ||
                e.target.closest('.modal-close')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });

        // ESCキーでモーダルを閉じる
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.show');
                if (activeModal) {
                    this.closeModal(activeModal);
                }
            }
        });
    }

    /**
     * モーダル開く
     */
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('show');
        document.body.style.overflow = 'hidden';

        // フォーカス管理
        const firstFocusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }

        // アニメーション
        const content = modal.querySelector('.modal-content');
        if (content) {
            content.classList.add('slide-in-up');
        }
    }

    /**
     * モーダル閉じる
     */
    closeModal(modal) {
        if (!modal) return;

        modal.classList.remove('show');
        document.body.style.overflow = '';

        const content = modal.querySelector('.modal-content');
        if (content) {
            content.classList.remove('slide-in-up');
        }
    }

    /**
     * 通知システム設定
     */
    setupNotifications() {
        // 通知コンテナ作成
        if (!document.querySelector('.notifications-container')) {
            const container = document.createElement('div');
            container.className = 'notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }

    /**
     * 通知表示
     */
    showNotification(message, type = 'info', duration = 4000) {
        const container = document.querySelector('.notifications-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: var(--color-white);
            color: var(--color-gray-900);
            padding: 16px 20px;
            margin-bottom: 8px;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            border-left: 4px solid var(--color-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'});
            transform: translateX(100%);
            transition: transform 0.3s ease;
            pointer-events: auto;
            max-width: 350px;
            word-wrap: break-word;
        `;

        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 8px;">${icon}</span>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()"
                        style="margin-left: auto; background: none; border: none; cursor: pointer; color: var(--color-gray-500);">
                    ✕
                </button>
            </div>
        `;

        container.appendChild(notification);

        // アニメーション
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 自動削除
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }
            }, duration);
        }

        this.notifications.push({
            element: notification,
            message,
            type,
            timestamp: Date.now()
        });
    }

    /**
     * 通知アイコン取得
     */
    getNotificationIcon(type) {
        const icons = {
            'success': '✓',
            'error': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        };
        return icons[type] || icons.info;
    }

    /**
     * ツールチップ設定
     */
    setupTooltips() {
        const tooltipElements = document.querySelectorAll('[title], [data-tooltip]');

        tooltipElements.forEach(element => {
            const tooltipText = element.getAttribute('data-tooltip') || element.getAttribute('title');
            if (!tooltipText) return;

            element.removeAttribute('title'); // デフォルトツールチップを無効化

            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, tooltipText);
            });

            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    /**
     * ツールチップ表示
     */
    showTooltip(element, text) {
        this.hideTooltip();

        const tooltip = document.createElement('div');
        tooltip.className = 'simple-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--color-gray-900);
            color: var(--color-white);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            white-space: nowrap;
            z-index: 10000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
        `;

        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        tooltip.style.left = `${rect.left + rect.width / 2 - tooltipRect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltipRect.height - 5}px`;

        setTimeout(() => {
            tooltip.style.opacity = '1';
        }, 100);

        this.currentTooltip = tooltip;
    }

    /**
     * ツールチップ非表示
     */
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    /**
     * アクセシビリティ設定
     */
    setupAccessibility() {
        // フォーカス表示の改善
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // スクリーンリーダー対応
        this.setupARIA();
    }

    /**
     * ARIA属性設定
     */
    setupARIA() {
        // ボタンにaria-labelを追加
        document.querySelectorAll('button:not([aria-label])').forEach(btn => {
            if (!btn.textContent.trim()) {
                const icon = btn.querySelector('i');
                if (icon) {
                    btn.setAttribute('aria-label', this.getIconLabel(icon.className));
                }
            }
        });

        // フォームにaria-requiredを追加
        document.querySelectorAll('input[required], select[required], textarea[required]').forEach(input => {
            input.setAttribute('aria-required', 'true');
        });
    }

    /**
     * アイコンラベル取得
     */
    getIconLabel(className) {
        const iconLabels = {
            'fa-home': 'ホーム',
            'fa-user': 'ユーザー',
            'fa-search': '検索',
            'fa-edit': '編集',
            'fa-trash': '削除',
            'fa-plus': '追加',
            'fa-save': '保存',
            'fa-close': '閉じる',
            'fa-check': 'チェック'
        };

        for (let iconClass in iconLabels) {
            if (className.includes(iconClass)) {
                return iconLabels[iconClass];
            }
        }

        return 'ボタン';
    }

    /**
     * キーボードショートカット
     */
    handleKeyboardShortcuts(e) {
        // Ctrl+S で保存
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitButton = activeForm.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }

        // Ctrl+/ でヘルプ
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            this.showHelp();
        }

        // Alt+M でメニュートグル（モバイル）
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            const menuToggle = document.querySelector('.menu-toggle');
            if (menuToggle) {
                menuToggle.click();
            }
        }
    }

    /**
     * ヘルプ表示
     */
    showHelp() {
        const helpModal = document.getElementById('help-modal');
        if (helpModal) {
            this.openModal('help-modal');
        } else {
            this.showNotification('Ctrl+S: 保存, ESC: モーダルを閉じる', 'info', 5000);
        }
    }

    /**
     * ページ読み込みアニメーション
     */
    showPageLoadAnimation() {
        const cards = document.querySelectorAll('.card, .dashboard-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * ナビゲーション処理
     */
    handleNavigation(e, link) {
        const href = link.getAttribute('href');

        // 外部リンクの場合はそのまま遷移
        if (href.startsWith('http')) {
            return;
        }

        // SPA風の遷移エフェクト
        if (link.hasAttribute('data-smooth-transition')) {
            e.preventDefault();
            this.smoothTransition(href);
        }
    }

    /**
     * スムーズ遷移
     */
    smoothTransition(href) {
        document.body.style.opacity = '0.5';
        document.body.style.transition = 'opacity 0.3s ease';

        setTimeout(() => {
            window.location.href = href;
        }, 300);
    }

    /**
     * ページプリロード
     */
    preloadPage(href) {
        if (href && !href.startsWith('http') && !this.preloadedPages.has(href)) {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = href;
            document.head.appendChild(link);
            this.preloadedPages.add(href);
        }
    }

    /**
     * リサイズ処理
     */
    handleResize() {
        // モバイル表示の切り替え
        const isMobile = window.innerWidth < 768;
        document.body.classList.toggle('mobile', isMobile);

        // ツールチップの位置調整
        this.hideTooltip();
    }

    /**
     * ローディング状態設定
     */
    setLoading(loading) {
        this.isLoading = loading;
        document.body.classList.toggle('loading', loading);
    }

    /**
     * フォーム変更マーク
     */
    markFormAsChanged() {
        this.hasChanges = true;
        window.onbeforeunload = () => '保存されていない変更があります。';
    }

    /**
     * フォーム保存マーク
     */
    markFormAsSaved() {
        this.hasChanges = false;
        window.onbeforeunload = null;
    }

    /**
     * 未保存変更チェック
     */
    hasUnsavedChanges() {
        return this.hasChanges;
    }

    /**
     * 自動保存設定
     */
    setupAutoSave() {
        this.preloadedPages = new Set();
        this.hasChanges = false;

        // 5分ごとにセッション維持
        setInterval(() => {
            this.pingServer();
        }, 300000);
    }

    /**
     * サーバー疎通確認
     */
    pingServer() {
        // セッション維持のダミー処理
        localStorage.setItem('last_ping', new Date().toISOString());
    }

    // ユーティリティメソッド

    /**
     * 遅延実行
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * デバウンス
     */
    debounce(func, wait) {
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

    /**
     * メールアドレス検証
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * 電話番号検証
     */
    isValidPhone(phone) {
        const re = /^[\d\-\(\)\+\s]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    /**
     * 日付フォーマット
     */
    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');

        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    }

    /**
     * 数値フォーマット（カンマ区切り）
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * 文字数制限
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * クッキー設定
     */
    setCookie(name, value, days = 7) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
    }

    /**
     * クッキー取得
     */
    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    /**
     * ローカルストレージ安全な設定
     */
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage quota exceeded');
        }
    }

    /**
     * ローカルストレージ安全な取得
     */
    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('LocalStorage parse error');
            return defaultValue;
        }
    }

    /**
     * パフォーマンス監視
     */
    measurePerformance(name, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${name}: ${end - start} milliseconds`);
        return result;
    }
}

/**
 * DOM読み込み完了時に初期化
 */
document.addEventListener('DOMContentLoaded', () => {
    window.simpleUI = new SimpleUI();
});

/**
 * エラーハンドリング
 */
window.addEventListener('error', (e) => {
    console.error('JavaScript Error:', e.error);
    if (window.simpleUI) {
        window.simpleUI.showNotification('システムエラーが発生しました', 'error');
    }
});

/**
 * 未処理のPromise拒否をキャッチ
 */
window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled Promise Rejection:', e.reason);
    if (window.simpleUI) {
        window.simpleUI.showNotification('処理中にエラーが発生しました', 'error');
    }
});

/**
 * グローバル関数エクスポート（レガシー互換性）
 */
window.showNotification = (message, type, duration) => {
    if (window.simpleUI) {
        window.simpleUI.showNotification(message, type, duration);
    }
};

window.openModal = (modalId) => {
    if (window.simpleUI) {
        window.simpleUI.openModal(modalId);
    }
};

window.closeModal = (modal) => {
    if (window.simpleUI) {
        window.simpleUI.closeModal(modal);
    }
};

// スタイルシート動的読み込み確認
if (!document.querySelector('link[href*="simple_theme.css"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'css/simple_theme.css';
    document.head.appendChild(link);
}