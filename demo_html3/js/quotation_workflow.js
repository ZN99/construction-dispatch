/**
 * 見積作成ワークフロー制御システム
 * 労働者派遣法第23条準拠
 */

class QuotationWorkflow {
    constructor() {
        this.currentCaseId = null;
        this.userRole = this.getUserRole();
        this.workflowSteps = [
            { id: 'room_survey', name: '現地調査', role: 'temporary' },
            { id: 'material_input', name: '材料費入力', role: 'both' },
            { id: 'margin_setting', name: 'マージン設定', role: 'employee' },
            { id: 'quotation_generate', name: '見積書生成', role: 'employee' }
        ];

        this.materialMaster = this.loadMaterialMaster();
        this.init();
    }

    /**
     * 初期化処理
     */
    init() {
        this.setupEventListeners();
        this.loadCurrentCase();
        this.checkNotifications();

        // 定期的なステータスチェック
        setInterval(() => {
            this.checkWorkflowUpdates();
        }, 30000); // 30秒毎

        // 法令遵守チェック
        this.enforceRoleCompliance();

        console.log('見積ワークフロー システム初期化完了');
    }

    /**
     * ユーザー役割の取得
     */
    getUserRole() {
        const bodyRole = document.body.getAttribute('data-user-role');
        return bodyRole || 'temporary'; // デフォルトは派遣スタッフ
    }

    /**
     * 役割遵守の強制実行
     */
    enforceRoleCompliance() {
        const currentPath = window.location.pathname;

        // 派遣スタッフの制限チェック
        if (this.userRole === 'temporary') {
            const restrictedPaths = ['/pricing/margin_setting.html'];
            if (restrictedPaths.some(path => currentPath.includes(path))) {
                this.logAuditEvent('UNAUTHORIZED_ACCESS_BLOCKED', currentPath, 'COMPLIANCE_VIOLATION');
                alert('このページへのアクセス権限がありません。');
                window.location.href = 'pricing/staff_status_view.html';
                return;
            }
        }

        this.logAuditEvent('ROLE_COMPLIANCE_CHECK', `Role: ${this.userRole}, Path: ${currentPath}`, 'COMPLIANCE_AUDIT');
    }

    /**
     * イベントリスナーの設定
     */
    setupEventListeners() {
        // ページ離脱時の自動保存
        window.addEventListener('beforeunload', () => {
            this.autoSave();
        });

        // フォーカス復帰時のデータ同期
        window.addEventListener('focus', () => {
            this.syncWorkflowData();
        });

        // オンライン/オフライン状態の監視
        window.addEventListener('online', () => {
            this.handleOnlineStatus(true);
        });

        window.addEventListener('offline', () => {
            this.handleOnlineStatus(false);
        });
    }

    /**
     * 新規案件の開始
     */
    startNewCase(customerInfo = {}) {
        const caseId = this.generateCaseId();
        const caseData = {
            caseId: caseId,
            status: 'room_survey',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            createdBy: this.userRole,
            customerInfo: customerInfo,
            workflow: {
                room_survey: { status: 'active', startedAt: new Date().toISOString() },
                material_input: { status: 'pending' },
                margin_setting: { status: 'pending' },
                quotation_generate: { status: 'pending' }
            }
        };

        this.saveWorkflowData(caseId, caseData);
        this.currentCaseId = caseId;

        this.logAuditEvent('NEW_CASE_STARTED', caseId, 'WORKFLOW_MANAGEMENT');
        this.sendNotification('新規案件が開始されました', `案件ID: ${caseId}`);

        return caseId;
    }

    /**
     * 案件IDの生成
     */
    generateCaseId() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const random = Math.random().toString(36).substr(2, 6).toUpperCase();

        return `Q${year}${month}${day}-${random}`;
    }

    /**
     * 部屋情報の送信
     */
    async submitRoomData(roomData) {
        if (this.userRole !== 'temporary' && this.userRole !== 'both') {
            throw new Error('派遣スタッフのみが現地調査データを入力できます');
        }

        try {
            const caseData = this.loadWorkflowData(this.currentCaseId);
            if (!caseData) {
                throw new Error('案件データが見つかりません');
            }

            // 部屋情報の保存
            caseData.roomData = {
                rooms: roomData,
                submittedAt: new Date().toISOString(),
                submittedBy: this.userRole
            };

            // ワークフロー進捗の更新
            caseData.workflow.room_survey.status = 'completed';
            caseData.workflow.room_survey.completedAt = new Date().toISOString();
            caseData.workflow.material_input.status = 'active';
            caseData.workflow.material_input.startedAt = new Date().toISOString();
            caseData.status = 'material_input';
            caseData.updatedAt = new Date().toISOString();

            this.saveWorkflowData(this.currentCaseId, caseData);

            // 社員への通知
            this.notifyEmployees('現地調査完了', `案件${this.currentCaseId}の現地調査が完了しました`);

            this.logAuditEvent('ROOM_DATA_SUBMITTED', this.currentCaseId, 'WORKFLOW_PROGRESS');

            return {
                success: true,
                nextStep: 'material_input',
                message: '現地調査データが正常に送信されました'
            };

        } catch (error) {
            this.logAuditEvent('ROOM_DATA_SUBMIT_ERROR', error.message, 'WORKFLOW_ERROR');
            throw error;
        }
    }

    /**
     * 材料費データの保存
     */
    async saveMaterialCosts(materialData) {
        try {
            const caseData = this.loadWorkflowData(this.currentCaseId);
            if (!caseData) {
                throw new Error('案件データが見つかりません');
            }

            // 材料費の計算
            const totalCost = this.calculateTotalCost(materialData);

            caseData.materialData = {
                materials: materialData,
                totalCost: totalCost,
                submittedAt: new Date().toISOString(),
                submittedBy: this.userRole
            };

            // ワークフロー進捗の更新
            caseData.workflow.material_input.status = 'completed';
            caseData.workflow.material_input.completedAt = new Date().toISOString();

            // 社員のみがマージン設定可能
            if (this.userRole === 'employee') {
                caseData.workflow.margin_setting.status = 'active';
                caseData.workflow.margin_setting.startedAt = new Date().toISOString();
                caseData.status = 'margin_setting';
            } else {
                caseData.status = 'employee_review';
            }

            caseData.updatedAt = new Date().toISOString();
            this.saveWorkflowData(this.currentCaseId, caseData);

            // 通知の送信
            if (this.userRole === 'temporary') {
                this.notifyEmployees('材料費入力完了', `案件${this.currentCaseId}の材料費入力が完了しました`);
                this.sendNotification('材料費入力完了', '社員の確認をお待ちください');
            } else {
                this.sendNotification('材料費入力完了', 'マージン設定を行ってください');
            }

            this.logAuditEvent('MATERIAL_COSTS_SAVED', this.currentCaseId, 'WORKFLOW_PROGRESS');

            return {
                success: true,
                totalCost: totalCost,
                nextStep: this.userRole === 'employee' ? 'margin_setting' : 'employee_review'
            };

        } catch (error) {
            this.logAuditEvent('MATERIAL_COSTS_SAVE_ERROR', error.message, 'WORKFLOW_ERROR');
            throw error;
        }
    }

    /**
     * マージン設定（社員のみ）
     */
    async setMargin(marginConfig) {
        if (this.userRole !== 'employee') {
            throw new Error('社員のみがマージンを設定できます（労働者派遣法第23条）');
        }

        try {
            const caseData = this.loadWorkflowData(this.currentCaseId);
            if (!caseData || !caseData.materialData) {
                throw new Error('材料費データが不足しています');
            }

            const baseCost = caseData.materialData.totalCost;
            const finalPrice = this.calculateFinalPrice(baseCost, marginConfig);

            caseData.marginData = {
                type: marginConfig.type, // 'rate' or 'amount'
                value: marginConfig.value,
                baseCost: baseCost,
                profitAmount: finalPrice - baseCost,
                finalPrice: finalPrice,
                setAt: new Date().toISOString(),
                setBy: this.userRole
            };

            // ワークフロー進捗の更新
            caseData.workflow.margin_setting.status = 'completed';
            caseData.workflow.margin_setting.completedAt = new Date().toISOString();
            caseData.workflow.quotation_generate.status = 'active';
            caseData.workflow.quotation_generate.startedAt = new Date().toISOString();
            caseData.status = 'quotation_generate';
            caseData.updatedAt = new Date().toISOString();

            this.saveWorkflowData(this.currentCaseId, caseData);

            // 派遣スタッフへの通知
            this.notifyTemporaryStaff('マージン設定完了', '見積書生成中です');

            this.logAuditEvent('MARGIN_SET',
                `Case: ${this.currentCaseId}, Type: ${marginConfig.type}, Value: ${marginConfig.value}`,
                'WORKFLOW_PROGRESS');

            return {
                success: true,
                finalPrice: finalPrice,
                profitAmount: finalPrice - baseCost,
                nextStep: 'quotation_generate'
            };

        } catch (error) {
            this.logAuditEvent('MARGIN_SET_ERROR', error.message, 'WORKFLOW_ERROR');
            throw error;
        }
    }

    /**
     * 見積書の生成
     */
    async generateQuotation() {
        if (this.userRole !== 'employee') {
            throw new Error('社員のみが見積書を生成できます');
        }

        try {
            const caseData = this.loadWorkflowData(this.currentCaseId);
            if (!caseData || !caseData.marginData) {
                throw new Error('マージンデータが不足しています');
            }

            const quotationData = this.buildQuotationData(caseData);

            caseData.quotationData = {
                ...quotationData,
                generatedAt: new Date().toISOString(),
                generatedBy: this.userRole,
                quotationId: this.generateQuotationId()
            };

            // ワークフロー完了
            caseData.workflow.quotation_generate.status = 'completed';
            caseData.workflow.quotation_generate.completedAt = new Date().toISOString();
            caseData.status = 'completed';
            caseData.completedAt = new Date().toISOString();
            caseData.updatedAt = new Date().toISOString();

            this.saveWorkflowData(this.currentCaseId, caseData);

            // 完了通知
            this.notifyAllParties('見積書生成完了', `案件${this.currentCaseId}の見積書が生成されました`);

            this.logAuditEvent('QUOTATION_GENERATED',
                `Case: ${this.currentCaseId}, Quotation: ${caseData.quotationData.quotationId}`,
                'WORKFLOW_COMPLETED');

            return {
                success: true,
                quotationId: caseData.quotationData.quotationId,
                quotationData: caseData.quotationData
            };

        } catch (error) {
            this.logAuditEvent('QUOTATION_GENERATE_ERROR', error.message, 'WORKFLOW_ERROR');
            throw error;
        }
    }

    /**
     * 最終価格の計算
     */
    calculateFinalPrice(baseCost, marginConfig) {
        let finalPrice;

        if (marginConfig.type === 'rate') {
            // 利益率での計算
            finalPrice = baseCost * (1 + marginConfig.value / 100);
        } else {
            // 利益額での計算
            finalPrice = baseCost + marginConfig.value;
        }

        // 消費税の追加
        const taxRate = 0.10; // 10%
        finalPrice = Math.round(finalPrice * (1 + taxRate));

        return finalPrice;
    }

    /**
     * 材料費合計の計算
     */
    calculateTotalCost(materials) {
        return materials.reduce((total, material) => {
            return total + (material.quantity * material.unitPrice);
        }, 0);
    }

    /**
     * 見積書データの構築
     */
    buildQuotationData(caseData) {
        const currentDate = new Date();
        const expiryDate = new Date(currentDate.getTime() + (30 * 24 * 60 * 60 * 1000)); // 30日後

        return {
            companyInfo: {
                name: '株式会社建築派遣SaaS',
                address: '東京都千代田区○○1-2-3',
                phone: '03-1234-5678',
                email: 'info@construction-saas.jp'
            },
            customerInfo: caseData.customerInfo,
            items: this.formatQuotationItems(caseData),
            subtotal: caseData.materialData.totalCost,
            tax: Math.round(caseData.marginData.finalPrice * 0.10 / 1.10),
            total: caseData.marginData.finalPrice,
            validUntil: expiryDate.toISOString().split('T')[0],
            paymentTerms: '工事完了後30日以内',
            notes: this.generateQuotationNotes(caseData)
        };
    }

    /**
     * 見積項目のフォーマット
     */
    formatQuotationItems(caseData) {
        const items = [];

        // 材料費項目
        if (caseData.materialData && caseData.materialData.materials) {
            caseData.materialData.materials.forEach(material => {
                items.push({
                    category: material.category,
                    name: material.name,
                    quantity: material.quantity,
                    unit: material.unit,
                    unitPrice: material.unitPrice,
                    amount: material.quantity * material.unitPrice
                });
            });
        }

        // 諸経費・利益
        const profitAmount = caseData.marginData.profitAmount;
        items.push({
            category: '諸経費',
            name: '管理費・利益',
            quantity: 1,
            unit: '式',
            unitPrice: profitAmount,
            amount: profitAmount
        });

        return items;
    }

    /**
     * 見積書備考の生成
     */
    generateQuotationNotes(caseData) {
        const notes = [
            '・上記金額は税込み価格です',
            '・工事期間は着工後3-5日を予定しています',
            '・材料費の変動により金額が変更になる場合があります',
            '・見積有効期限は発行日より30日間です'
        ];

        if (caseData.roomData && caseData.roomData.rooms) {
            const roomCount = caseData.roomData.rooms.length;
            notes.push(`・対象部屋数: ${roomCount}室`);
        }

        return notes;
    }

    /**
     * 見積書IDの生成
     */
    generateQuotationId() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const serial = Math.random().toString(36).substr(2, 4).toUpperCase();

        return `EST-${year}${month}${day}-${serial}`;
    }

    /**
     * ワークフローステータスの更新
     */
    updateStatus(caseId, newStatus) {
        const caseData = this.loadWorkflowData(caseId);
        if (caseData) {
            caseData.status = newStatus;
            caseData.updatedAt = new Date().toISOString();
            this.saveWorkflowData(caseId, caseData);

            this.logAuditEvent('STATUS_UPDATED', `Case: ${caseId}, Status: ${newStatus}`, 'WORKFLOW_STATUS');

            // UI更新イベントの発火
            this.dispatchStatusUpdateEvent(caseId, newStatus);
        }
    }

    /**
     * ステータス更新イベントの発火
     */
    dispatchStatusUpdateEvent(caseId, newStatus) {
        const event = new CustomEvent('workflowStatusUpdate', {
            detail: { caseId, newStatus }
        });
        window.dispatchEvent(event);
    }

    /**
     * データの保存
     */
    saveWorkflowData(caseId, data) {
        try {
            localStorage.setItem(`workflow_${caseId}`, JSON.stringify(data));
            localStorage.setItem('current_case_id', caseId);

            // バックアップ保存
            this.saveToIndexedDB(caseId, data);

        } catch (error) {
            console.error('データ保存エラー:', error);
            this.logAuditEvent('DATA_SAVE_ERROR', error.message, 'SYSTEM_ERROR');
        }
    }

    /**
     * データの読み込み
     */
    loadWorkflowData(caseId) {
        try {
            const data = localStorage.getItem(`workflow_${caseId}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('データ読み込みエラー:', error);
            this.logAuditEvent('DATA_LOAD_ERROR', error.message, 'SYSTEM_ERROR');
            return null;
        }
    }

    /**
     * 現在の案件の読み込み
     */
    loadCurrentCase() {
        const caseId = localStorage.getItem('current_case_id');
        if (caseId) {
            this.currentCaseId = caseId;
            return this.loadWorkflowData(caseId);
        }
        return null;
    }

    /**
     * 材料マスターの読み込み
     */
    loadMaterialMaster() {
        return {
            flooring: [
                { name: 'フローリング材A', unitPrice: 8000, unit: '㎡' },
                { name: 'フローリング材B', unitPrice: 6500, unit: '㎡' },
                { name: 'クッションフロア', unitPrice: 4500, unit: '㎡' }
            ],
            wallpaper: [
                { name: '壁紙（スタンダード）', unitPrice: 1800, unit: '㎡' },
                { name: '壁紙（防汚加工）', unitPrice: 2200, unit: '㎡' },
                { name: '壁紙（高級品）', unitPrice: 3500, unit: '㎡' }
            ],
            labor: [
                { name: 'クリーニング作業', unitPrice: 2800, unit: '㎡' },
                { name: '壁紙張替工事', unitPrice: 3200, unit: '㎡' },
                { name: '設備清掃', unitPrice: 2500, unit: '台' }
            ]
        };
    }

    /**
     * 自動保存
     */
    autoSave() {
        if (this.currentCaseId) {
            const currentData = this.loadWorkflowData(this.currentCaseId);
            if (currentData) {
                currentData.lastAutoSave = new Date().toISOString();
                this.saveWorkflowData(this.currentCaseId, currentData);
            }
        }
    }

    /**
     * データ同期
     */
    async syncWorkflowData() {
        // 実際の実装では、サーバーとの同期処理
        console.log('ワークフローデータ同期中...');
    }

    /**
     * オンライン/オフライン状態の処理
     */
    handleOnlineStatus(isOnline) {
        if (isOnline) {
            this.syncWorkflowData();
            this.sendNotification('接続復旧', 'サーバーとの接続が復旧しました');
        } else {
            this.sendNotification('オフライン', 'データはローカルに保存されています');
        }
    }

    /**
     * 社員への通知
     */
    notifyEmployees(title, message) {
        if (this.userRole === 'employee') return; // 自分自身には通知しない

        this.sendNotification(title, message, 'employee');
        this.logAuditEvent('EMPLOYEE_NOTIFICATION', `Title: ${title}, Message: ${message}`, 'NOTIFICATION');
    }

    /**
     * 派遣スタッフへの通知
     */
    notifyTemporaryStaff(title, message) {
        if (this.userRole === 'temporary') return; // 自分自身には通知しない

        this.sendNotification(title, message, 'temporary');
        this.logAuditEvent('TEMPORARY_NOTIFICATION', `Title: ${title}, Message: ${message}`, 'NOTIFICATION');
    }

    /**
     * 全関係者への通知
     */
    notifyAllParties(title, message) {
        this.sendNotification(title, message, 'all');
        this.logAuditEvent('ALL_NOTIFICATION', `Title: ${title}, Message: ${message}`, 'NOTIFICATION');
    }

    /**
     * 通知の送信
     */
    sendNotification(title, message, target = 'current') {
        // ブラウザ通知
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/favicon.ico',
                badge: '/favicon.ico'
            });
        }

        // 画面内通知
        this.showInAppNotification(title, message);

        // 音声アラート
        this.playNotificationSound();
    }

    /**
     * 画面内通知の表示
     */
    showInAppNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
        notification.innerHTML = `
            <strong>${title}</strong><br>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * 通知音の再生
     */
    playNotificationSound() {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj...');
        audio.volume = 0.1;
        audio.play().catch(() => {}); // 音声再生失敗は無視
    }

    /**
     * 通知チェック
     */
    checkNotifications() {
        // ブラウザ通知の許可を要求
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    /**
     * ワークフロー更新のチェック
     */
    checkWorkflowUpdates() {
        if (!this.currentCaseId) return;

        const currentData = this.loadWorkflowData(this.currentCaseId);
        if (currentData) {
            const event = new CustomEvent('workflowDataUpdate', {
                detail: { caseId: this.currentCaseId, data: currentData }
            });
            window.dispatchEvent(event);
        }
    }

    /**
     * IndexedDBへの保存（バックアップ）
     */
    async saveToIndexedDB(caseId, data) {
        try {
            if (!window.indexedDB) return;

            const request = indexedDB.open('QuotationWorkflow', 1);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('cases')) {
                    db.createObjectStore('cases', { keyPath: 'caseId' });
                }
            };

            request.onsuccess = (event) => {
                const db = event.target.result;
                const transaction = db.transaction(['cases'], 'readwrite');
                const store = transaction.objectStore('cases');
                store.put(data);
            };

        } catch (error) {
            console.error('IndexedDB保存エラー:', error);
        }
    }

    /**
     * 監査ログの記録
     */
    logAuditEvent(action, details, category) {
        const auditLog = {
            timestamp: new Date().toISOString(),
            action: action,
            details: details,
            category: category,
            caseId: this.currentCaseId,
            userId: 'current_user',
            userRole: this.userRole,
            module: 'quotation_workflow'
        };

        // ローカルストレージに保存
        const auditLogs = JSON.parse(localStorage.getItem('audit_logs') || '[]');
        auditLogs.push(auditLog);

        // 最新1000件のみ保持
        if (auditLogs.length > 1000) {
            auditLogs.splice(0, auditLogs.length - 1000);
        }

        localStorage.setItem('audit_logs', JSON.stringify(auditLogs));

        console.log('ワークフロー監査ログ:', auditLog);
    }

    /**
     * 進捗率の計算
     */
    calculateProgress() {
        if (!this.currentCaseId) return 0;

        const caseData = this.loadWorkflowData(this.currentCaseId);
        if (!caseData) return 0;

        const completedSteps = Object.values(caseData.workflow)
            .filter(step => step.status === 'completed').length;

        return Math.round((completedSteps / this.workflowSteps.length) * 100);
    }

    /**
     * エラーハンドリング
     */
    handleError(error, context = '') {
        console.error(`ワークフローエラー${context ? ' - ' + context : ''}:`, error);

        this.logAuditEvent('WORKFLOW_ERROR',
            `Context: ${context}, Error: ${error.message}`,
            'SYSTEM_ERROR');

        this.sendNotification('エラー',
            `処理中にエラーが発生しました${context ? ' (' + context + ')' : ''}`);
    }
}

// グローバルインスタンスの作成
window.quotationWorkflow = new QuotationWorkflow();

// DOMContentLoadedイベントでの初期化
document.addEventListener('DOMContentLoaded', () => {
    if (!window.quotationWorkflow) {
        window.quotationWorkflow = new QuotationWorkflow();
    }
});

// エクスポート（モジュール対応）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuotationWorkflow;
}