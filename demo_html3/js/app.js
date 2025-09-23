// 建築派遣SaaS - メインアプリケーション

class ConstructionSaaS {
    constructor() {
        this.projects = this.loadDemoData();
        this.surveys = this.loadSurveyData();
        this.craftsmen = this.loadCraftsmenData();
        this.auditTrail = this.loadAuditTrail();
        this.currentUser = this.getCurrentUser();
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    // Phase 4: 監査証跡管理
    loadAuditTrail() {
        return JSON.parse(localStorage.getItem('auditTrail')) || [];
    }

    saveAuditTrail() {
        localStorage.setItem('auditTrail', JSON.stringify(this.auditTrail));
    }

    getCurrentUser() {
        return {
            id: localStorage.getItem('userId') || 'user_001',
            name: localStorage.getItem('userName') || '管理者',
            role: localStorage.getItem('userRole') || 'employee',
            ipAddress: '192.168.1.100', // 実際は動的に取得
            sessionId: this.generateSessionId()
        };
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // 監査ログ記録
    logAuditEvent(action, details = {}) {
        const auditEvent = {
            id: 'audit_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
            timestamp: new Date().toISOString(),
            userId: this.currentUser.id,
            userName: this.currentUser.name,
            userRole: this.currentUser.role,
            action: action,
            details: details,
            ipAddress: this.currentUser.ipAddress,
            sessionId: this.currentUser.sessionId,
            page: this.currentPage,
            userAgent: navigator.userAgent
        };

        this.auditTrail.unshift(auditEvent);

        // 最新の1000件のみ保持
        if (this.auditTrail.length > 1000) {
            this.auditTrail = this.auditTrail.slice(0, 1000);
        }

        this.saveAuditTrail();

        // コンプライアンス要件: 重要操作は即座に外部ログに送信
        if (this.isCriticalAction(action)) {
            this.sendCriticalAuditToExternalLog(auditEvent);
        }

        return auditEvent.id;
    }

    isCriticalAction(action) {
        const criticalActions = [
            'USER_LOGIN',
            'USER_LOGOUT',
            'PROJECT_APPROVED',
            'PROJECT_REJECTED',
            'SURVEY_COMPLETED',
            'CONTRACTOR_APPROVED',
            'PRICING_APPROVED',
            'ROLE_CHANGED',
            'DATA_EXPORT',
            'SYSTEM_CONFIG_CHANGED'
        ];
        return criticalActions.includes(action);
    }

    sendCriticalAuditToExternalLog(auditEvent) {
        // 実際の実装では外部監査システムに送信
        console.log('🔒 Critical Audit Event:', auditEvent);

        // 労働者派遣法・労働安全衛生法対応のための詳細ログ
        if (auditEvent.action.includes('SURVEY') || auditEvent.action.includes('CONTRACTOR')) {
            console.log('📋 Labor Law Compliance Log:', {
                event: auditEvent,
                legalCompliance: '労働者派遣法第23条対応',
                safetyCompliance: '労働安全衛生法第28条対応'
            });
        }
    }

    // 役割分離に基づく権限チェック
    checkPermission(action) {
        const permissions = {
            'employee': [
                'CREATE_PROJECT', 'APPROVE_PROJECT', 'DELETE_PROJECT',
                'CREATE_SURVEY', 'APPROVE_SURVEY', 'VIEW_PRICING',
                'MANAGE_CONTRACTORS', 'VIEW_AUDIT_TRAIL', 'EXPORT_DATA'
            ],
            'temporary_staff': [
                'EXECUTE_SURVEY', 'UPDATE_SURVEY_DATA', 'VIEW_SCHEDULE',
                'CONTACT_CONTRACTORS', 'VIEW_BASIC_PROJECT_INFO'
            ]
        };

        const userPermissions = permissions[this.currentUser.role] || [];
        const hasPermission = userPermissions.includes(action);

        // 権限チェックもログに記録
        this.logAuditEvent('PERMISSION_CHECK', {
            action: action,
            granted: hasPermission,
            reason: hasPermission ? 'Role-based access granted' : 'Insufficient permissions'
        });

        return hasPermission;
    }

    // データアクセス制御
    enforceDataAccess(operation, data, requiredRole = 'employee') {
        if (this.currentUser.role !== requiredRole) {
            this.logAuditEvent('ACCESS_DENIED', {
                operation: operation,
                data: typeof data === 'object' ? Object.keys(data) : data,
                requiredRole: requiredRole,
                userRole: this.currentUser.role
            });
            throw new Error('Access denied: Insufficient role privileges');
        }

        this.logAuditEvent('DATA_ACCESS', {
            operation: operation,
            dataAccessed: typeof data === 'object' ? Object.keys(data).length + ' records' : data
        });

        return true;
    }

    init() {
        // システム起動ログ
        this.logAuditEvent('SYSTEM_STARTUP', {
            page: this.currentPage,
            timestamp: new Date().toISOString()
        });

        this.setupEventListeners();
        this.initPageSpecificFeatures();
        this.startRealTimeUpdates();
        this.initializeCommonFeatures();
    }

    // Phase 4: 共通機能初期化
    initializeCommonFeatures() {
        this.setupGlobalErrorHandling();
        this.setupSessionManagement();
        this.setupDataValidation();
        this.setupSecurityFeatures();
    }

    // グローバルエラーハンドリング
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            this.logAuditEvent('SYSTEM_ERROR', {
                error: event.error?.message || 'Unknown error',
                stack: event.error?.stack || 'No stack trace',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.logAuditEvent('PROMISE_REJECTION', {
                reason: event.reason?.message || event.reason || 'Unknown rejection'
            });
        });
    }

    // セッション管理
    setupSessionManagement() {
        // セッション開始
        this.logAuditEvent('SESSION_START', {
            sessionId: this.currentUser.sessionId
        });

        // 非アクティブ検出（30分）
        let inactivityTimer;
        const resetInactivityTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                this.handleSessionTimeout();
            }, 30 * 60 * 1000); // 30分
        };

        // ユーザーアクティビティの監視
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetInactivityTimer, true);
        });

        resetInactivityTimer();

        // ページアンロード時
        window.addEventListener('beforeunload', () => {
            this.logAuditEvent('SESSION_END', {
                sessionId: this.currentUser.sessionId,
                duration: Date.now() - parseInt(this.currentUser.sessionId.split('_')[1])
            });
        });
    }

    handleSessionTimeout() {
        this.logAuditEvent('SESSION_TIMEOUT', {
            sessionId: this.currentUser.sessionId
        });

        alert('セッションがタイムアウトしました。再度ログインしてください。');

        // 実際の実装ではログイン画面にリダイレクト
        window.location.href = 'login.html';
    }

    // データバリデーション
    setupDataValidation() {
        this.dataValidationRules = {
            project: {
                name: { required: true, minLength: 3, maxLength: 100 },
                budget: { required: true, min: 1000, max: 10000000 },
                location: { required: true, minLength: 5, maxLength: 200 }
            },
            survey: {
                duration: { required: true, min: 30, max: 480 },
                scheduledDate: { required: true, dateFormat: true }
            },
            contractor: {
                name: { required: true, minLength: 2, maxLength: 50 },
                contact: { required: true, phoneFormat: true }
            }
        };
    }

    validateData(type, data) {
        const rules = this.dataValidationRules[type];
        if (!rules) return { valid: true };

        const errors = [];

        for (const [field, rule] of Object.entries(rules)) {
            const value = data[field];

            if (rule.required && (!value || value.toString().trim() === '')) {
                errors.push(`${field}は必須です`);
                continue;
            }

            if (value) {
                if (rule.minLength && value.toString().length < rule.minLength) {
                    errors.push(`${field}は${rule.minLength}文字以上で入力してください`);
                }
                if (rule.maxLength && value.toString().length > rule.maxLength) {
                    errors.push(`${field}は${rule.maxLength}文字以下で入力してください`);
                }
                if (rule.min && Number(value) < rule.min) {
                    errors.push(`${field}は${rule.min}以上で入力してください`);
                }
                if (rule.max && Number(value) > rule.max) {
                    errors.push(`${field}は${rule.max}以下で入力してください`);
                }
                if (rule.phoneFormat && !this.isValidPhone(value)) {
                    errors.push(`${field}の形式が正しくありません`);
                }
                if (rule.dateFormat && !this.isValidDate(value)) {
                    errors.push(`${field}の日付形式が正しくありません`);
                }
            }
        }

        const isValid = errors.length === 0;

        // バリデーション結果をログに記録
        this.logAuditEvent('DATA_VALIDATION', {
            type: type,
            valid: isValid,
            errors: errors,
            fieldCount: Object.keys(data).length
        });

        return { valid: isValid, errors: errors };
    }

    isValidPhone(phone) {
        const phoneRegex = /^[\d\-\(\)\+\s]+$/;
        return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    isValidDate(date) {
        const dateObj = new Date(date);
        return dateObj instanceof Date && !isNaN(dateObj);
    }

    // セキュリティ機能
    setupSecurityFeatures() {
        // CSRFトークン生成（模擬）
        this.csrfToken = this.generateCSRFToken();

        // XSS防止のための入力サニタイズ
        this.setupInputSanitization();

        // 不正アクセス監視
        this.setupAccessMonitoring();
    }

    generateCSRFToken() {
        return 'csrf_' + Date.now() + '_' + Math.random().toString(36).substr(2, 16);
    }

    setupInputSanitization() {
        // 入力フィールドのサニタイズ
        document.addEventListener('input', (event) => {
            if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
                const sanitized = this.sanitizeInput(event.target.value);
                if (sanitized !== event.target.value) {
                    this.logAuditEvent('INPUT_SANITIZED', {
                        field: event.target.name || event.target.id,
                        originalLength: event.target.value.length,
                        sanitizedLength: sanitized.length
                    });
                }
            }
        });
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;

        // 基本的なXSS攻撃文字列を除去
        return input
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '');
    }

    setupAccessMonitoring() {
        // 連続失敗試行の監視
        this.failedAttempts = parseInt(localStorage.getItem('failedAttempts')) || 0;

        // 異常なリクエストパターンの検出
        this.requestPattern = [];
    }

    recordFailedAttempt(operation) {
        this.failedAttempts++;
        localStorage.setItem('failedAttempts', this.failedAttempts.toString());

        this.logAuditEvent('FAILED_ATTEMPT', {
            operation: operation,
            failedAttempts: this.failedAttempts,
            timestamp: new Date().toISOString()
        });

        if (this.failedAttempts >= 5) {
            this.logAuditEvent('ACCOUNT_LOCKED', {
                reason: 'Multiple failed attempts',
                failedAttempts: this.failedAttempts
            });

            alert('アカウントが一時的にロックされました。管理者にお問い合わせください。');
        }
    }

    resetFailedAttempts() {
        this.failedAttempts = 0;
        localStorage.removeItem('failedAttempts');
    }

    // 監査ログ表示機能（管理者用）
    getAuditTrail(filters = {}) {
        if (!this.checkPermission('VIEW_AUDIT_TRAIL')) {
            throw new Error('監査ログの閲覧権限がありません');
        }

        let filteredLogs = [...this.auditTrail];

        // フィルタ適用
        if (filters.startDate) {
            filteredLogs = filteredLogs.filter(log =>
                new Date(log.timestamp) >= new Date(filters.startDate)
            );
        }

        if (filters.endDate) {
            filteredLogs = filteredLogs.filter(log =>
                new Date(log.timestamp) <= new Date(filters.endDate)
            );
        }

        if (filters.userId) {
            filteredLogs = filteredLogs.filter(log => log.userId === filters.userId);
        }

        if (filters.action) {
            filteredLogs = filteredLogs.filter(log => log.action.includes(filters.action));
        }

        this.logAuditEvent('AUDIT_TRAIL_VIEWED', {
            filters: filters,
            resultCount: filteredLogs.length
        });

        return filteredLogs;
    }

    // データエクスポート機能
    exportAuditData(format = 'json') {
        if (!this.checkPermission('EXPORT_DATA')) {
            this.recordFailedAttempt('EXPORT_DATA');
            throw new Error('データエクスポート権限がありません');
        }

        const exportData = {
            exportedAt: new Date().toISOString(),
            exportedBy: this.currentUser.name,
            totalRecords: this.auditTrail.length,
            data: this.auditTrail
        };

        this.logAuditEvent('DATA_EXPORT', {
            format: format,
            recordCount: this.auditTrail.length,
            exportSize: JSON.stringify(exportData).length
        });

        if (format === 'json') {
            return JSON.stringify(exportData, null, 2);
        } else if (format === 'csv') {
            return this.convertToCSV(exportData.data);
        }

        throw new Error('サポートされていないエクスポート形式です');
    }

    convertToCSV(data) {
        if (!data.length) return '';

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(field => {
                const value = row[field];
                return typeof value === 'string' && value.includes(',')
                    ? `"${value}"`
                    : value;
            }).join(','))
        ].join('\n');

        return csvContent;
    }

    // データローディング
    loadDemoData() {
        return [
            {
                id: 1,
                name: "新宿賃貸物件クロス張り替え",
                customer: "東京クロス工業",
                category: "cleaning",
                status: "in_progress",
                budget: 500000,
                progress: 60,
                created: "2025-09-10",
                location: "新宿区西新宿1-1-1"
            },
            {
                id: 2,
                name: "渋谷賃貸物件水道修理",
                customer: "都市部水道サービス",
                category: "plumbing",
                status: "survey",
                budget: 800000,
                progress: 30,
                created: "2025-09-12",
                location: "渋谷区道玄坂2-2-2"
            },
            {
                id: 3,
                name: "六本木賃貸原状回復工事",
                customer: "原状回復プロ",
                category: "interior",
                status: "completed",
                budget: 1200000,
                progress: 100,
                created: "2025-09-01",
                location: "港区六本木6-6-6"
            },
            {
                id: 4,
                name: "品川賃貸ハウスクリーニング",
                customer: "クリーニングマスター",
                category: "electrical",
                status: "scheduled",
                budget: 600000,
                progress: 10,
                created: "2025-09-14",
                location: "品川区大井1-1-1"
            },
            {
                id: 5,
                name: "池袋賃貸物件クロス張り替え",
                customer: "東京クロス工業",
                category: "cleaning",
                status: "in_progress",
                budget: 300000,
                progress: 45,
                created: "2025-09-08",
                location: "豊島区南池袋2-2-2"
            }
        ];
    }

    loadSurveyData() {
        return [
            {
                id: 1,
                projectId: 1,
                surveyor: "田中太郎",
                scheduledDate: "2025-09-15",
                startTime: "10:00",
                endTime: "12:00",
                status: "in_progress",
                progress: 60,
                duration: 120
            },
            {
                id: 2,
                projectId: 2,
                surveyor: "佐藤花子",
                scheduledDate: "2025-09-15",
                startTime: "14:30",
                endTime: "16:30",
                status: "scheduled",
                progress: 0,
                duration: 120
            },
            {
                id: 3,
                projectId: 3,
                surveyor: "鈴木一郎",
                scheduledDate: "2025-09-14",
                startTime: "09:00",
                endTime: "11:30",
                status: "completed",
                progress: 100,
                duration: 150
            },
            {
                id: 4,
                projectId: 4,
                surveyor: "田中太郎",
                scheduledDate: "2025-09-16",
                startTime: "13:00",
                endTime: "15:00",
                status: "scheduled",
                progress: 0,
                duration: 120
            }
        ];
    }

    loadCraftsmenData() {
        return [
            {
                id: 1,
                name: "田中太郎",
                skill: "クロス張り",
                level: "上級",
                status: "稼働中",
                rating: 4.8,
                experience: 5,
                contactEmail: "tanaka@example.com",
                phone: "090-1111-1111"
            },
            {
                id: 2,
                name: "佐藤花子",
                skill: "水道設備",
                level: "上級",
                status: "空き",
                rating: 4.9,
                experience: 8,
                contactEmail: "sato@example.com",
                phone: "090-2222-2222"
            },
            {
                id: 3,
                name: "鈴木一郎",
                skill: "原状回復",
                level: "中級",
                status: "空き",
                rating: 4.6,
                experience: 3,
                contactEmail: "suzuki@example.com",
                phone: "090-3333-3333"
            },
            {
                id: 4,
                name: "高橋美咲",
                skill: "クリーニング",
                level: "上級",
                status: "空き",
                rating: 4.7,
                experience: 6,
                contactEmail: "takahashi@example.com",
                phone: "090-4444-4444"
            },
            {
                id: 5,
                name: "伊藤健太",
                skill: "クロス張り",
                level: "中級",
                status: "稼働中",
                rating: 4.3,
                experience: 2,
                contactEmail: "ito@example.com",
                phone: "090-5555-5555"
            }
        ];
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('project_list')) return 'project_list';
        if (path.includes('project_detail')) return 'project_detail';
        if (path.includes('survey_list')) return 'survey_list';
        if (path.includes('craftsman_list')) return 'craftsman_list';
        if (path.includes('index')) return 'dashboard';
        return 'dashboard';
    }

    setupEventListeners() {
        // 検索機能
        const searchInput = document.getElementById('search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // フィルター機能
        const statusFilter = document.getElementById('status');
        const categoryFilter = document.getElementById('category');
        const statusFilterSurvey = document.getElementById('statusFilter');
        const surveyorFilter = document.getElementById('surveyorFilter');
        const dateFilter = document.getElementById('dateFilter');

        if (statusFilter) statusFilter.addEventListener('change', () => this.applyFilters());
        if (categoryFilter) categoryFilter.addEventListener('change', () => this.applyFilters());
        if (statusFilterSurvey) statusFilterSurvey.addEventListener('change', () => this.applySurveyFilters());
        if (surveyorFilter) surveyorFilter.addEventListener('change', () => this.applySurveyFilters());
        if (dateFilter) dateFilter.addEventListener('change', () => this.applySurveyFilters());

        // フォーム送信
        const searchForm = document.querySelector('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyFilters();
            });
        }

        // カード統計のクリック機能
        this.setupStatisticsCards();

        // リアルタイム更新
        this.setupRealTimeFeatures();
    }

    initPageSpecificFeatures() {
        switch (this.currentPage) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'project_list':
                this.initProjectList();
                break;
            case 'survey_list':
                this.initSurveyList();
                break;
            case 'craftsman_list':
                this.initCraftsmanList();
                break;
        }
    }

    // ダッシュボード初期化
    initDashboard() {
        this.updateDashboardStats();
        this.animateProgressBars();
        this.startDashboardUpdates();
    }

    updateDashboardStats() {
        const totalProjects = this.projects.length;
        const completedProjects = this.projects.filter(p => p.status === 'completed').length;
        const inProgressProjects = this.projects.filter(p => p.status === 'in_progress').length;
        const activeCraftsmen = this.craftsmen.filter(c => c.status === '稼働中').length;

        this.updateStatCard('.card.bg-primary h3', totalProjects);
        this.updateStatCard('.card.bg-success h3', completedProjects);
        this.updateStatCard('.card.bg-warning h3', inProgressProjects);
        this.updateStatCard('.card.bg-info h3', activeCraftsmen);
    }

    updateStatCard(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    }

    // プロジェクト一覧初期化
    initProjectList() {
        this.renderProjectStats();
        this.renderProjectTable();
    }

    renderProjectStats() {
        const stats = this.calculateProjectStats();
        this.updateStatCard('.border-primary .card-title', stats.total);
        this.updateStatCard('.border-warning .card-title', stats.inProgress);
        this.updateStatCard('.border-info .card-title', stats.survey);
        this.updateStatCard('.border-success .card-title', stats.completed);
    }

    calculateProjectStats() {
        return {
            total: this.projects.length,
            inProgress: this.projects.filter(p => p.status === 'in_progress').length,
            survey: this.projects.filter(p => p.status === 'survey').length,
            completed: this.projects.filter(p => p.status === 'completed').length
        };
    }

    // 調査一覧初期化
    initSurveyList() {
        this.renderSurveyStats();
        this.renderTodaysSurveys();
        this.renderSurveyTable();
    }

    renderSurveyStats() {
        const stats = this.calculateSurveyStats();
        this.updateStatCard('.border-info .card-title', stats.total);
        this.updateStatCard('.border-warning .card-title', stats.inProgress);
        this.updateStatCard('.border-secondary .card-title', stats.scheduled);
        this.updateStatCard('.border-success .card-title', stats.completed);
    }

    calculateSurveyStats() {
        return {
            total: this.surveys.length,
            inProgress: this.surveys.filter(s => s.status === 'in_progress').length,
            scheduled: this.surveys.filter(s => s.status === 'scheduled').length,
            completed: this.surveys.filter(s => s.status === 'completed').length
        };
    }

    // 職人一覧初期化
    initCraftsmanList() {
        this.renderCraftsmanTable();
        this.addCraftsmanFilters();
    }

    renderCraftsmanTable() {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        tbody.innerHTML = this.craftsmen.map(craftsman => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-circle me-2">
                            ${craftsman.name.charAt(0)}
                        </div>
                        <div>
                            <div class="fw-bold">${craftsman.name}</div>
                            <small class="text-muted">${craftsman.contactEmail}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${this.getSkillColor(craftsman.skill)}">${craftsman.skill}</span>
                    <br><small class="text-muted">経験 ${craftsman.experience}年</small>
                </td>
                <td>
                    <span class="badge bg-${this.getLevelColor(craftsman.level)}">${craftsman.level}</span>
                    <div class="rating mt-1">
                        ${this.renderStars(craftsman.rating)}
                        <small class="text-muted ms-1">(${craftsman.rating})</small>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${this.getStatusColor(craftsman.status)}">${craftsman.status}</span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="craftsman_detail.html?id=${craftsman.id}" class="btn btn-outline-primary">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="schedule_check.html?id=${craftsman.id}" class="btn btn-outline-warning">
                            <i class="fas fa-calendar-check"></i>
                        </a>
                        <button class="btn btn-outline-info" onclick="app.contactCraftsman(${craftsman.id})">
                            <i class="fas fa-phone"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="app.assignCraftsman(${craftsman.id})">
                            <i class="fas fa-user-plus"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getSkillColor(skill) {
        const colors = {
            'クロス張り': 'info',
            '水道設備': 'primary',
            '原状回復': 'warning',
            'クリーニング': 'danger'
        };
        return colors[skill] || 'secondary';
    }

    getLevelColor(level) {
        const colors = {
            '上級': 'success',
            '中級': 'info',
            '初級': 'warning'
        };
        return colors[level] || 'secondary';
    }

    getStatusColor(status) {
        const colors = {
            '稼働中': 'warning',
            '空き': 'success',
            '休暇中': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        let stars = '';

        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star text-warning"></i>';
        }

        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt text-warning"></i>';
        }

        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star text-muted"></i>';
        }

        return stars;
    }

    // 検索・フィルター機能
    handleSearch(query) {
        if (this.currentPage === 'project_list') {
            this.searchProjects(query);
        } else if (this.currentPage === 'craftsman_list') {
            this.searchCraftsmen(query);
        }
    }

    searchProjects(query) {
        const filteredProjects = this.projects.filter(project =>
            project.name.toLowerCase().includes(query.toLowerCase()) ||
            project.customer.toLowerCase().includes(query.toLowerCase())
        );
        this.renderFilteredProjects(filteredProjects);
    }

    searchCraftsmen(query) {
        const filteredCraftsmen = this.craftsmen.filter(craftsman =>
            craftsman.name.toLowerCase().includes(query.toLowerCase()) ||
            craftsman.skill.toLowerCase().includes(query.toLowerCase())
        );
        this.renderFilteredCraftsmen(filteredCraftsmen);
    }

    applyFilters() {
        if (this.currentPage !== 'project_list') return;

        const statusFilter = document.getElementById('status')?.value || '';
        const categoryFilter = document.getElementById('category')?.value || '';
        const searchQuery = document.getElementById('search')?.value || '';

        let filtered = this.projects;

        if (searchQuery) {
            filtered = filtered.filter(p =>
                p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                p.customer.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        if (statusFilter) {
            filtered = filtered.filter(p => p.status === statusFilter);
        }

        if (categoryFilter) {
            filtered = filtered.filter(p => p.category === categoryFilter);
        }

        this.renderFilteredProjects(filtered);
    }

    applySurveyFilters() {
        if (this.currentPage !== 'survey_list') return;

        const statusFilter = document.getElementById('statusFilter')?.value || '';
        const surveyorFilter = document.getElementById('surveyorFilter')?.value || '';
        const dateFilter = document.getElementById('dateFilter')?.value || '';

        let filtered = this.surveys;

        if (statusFilter) {
            filtered = filtered.filter(s => s.status === statusFilter);
        }

        if (surveyorFilter) {
            filtered = filtered.filter(s => s.surveyor.includes(surveyorFilter));
        }

        if (dateFilter) {
            filtered = filtered.filter(s => s.scheduledDate === dateFilter);
        }

        this.renderFilteredSurveys(filtered);
    }

    // アニメーション機能
    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1.5s ease-in-out';
                bar.style.width = width;
            }, 100);
        });
    }

    // リアルタイム更新
    startRealTimeUpdates() {
        // 5秒ごとに進捗バーを微調整
        setInterval(() => {
            this.simulateProgressUpdates();
        }, 5000);

        // 10秒ごとに統計を更新
        setInterval(() => {
            this.updateAllStats();
        }, 10000);
    }

    simulateProgressUpdates() {
        const inProgressProjects = this.projects.filter(p => p.status === 'in_progress');
        inProgressProjects.forEach(project => {
            if (Math.random() > 0.7) {
                project.progress = Math.min(project.progress + Math.floor(Math.random() * 3), 100);
                if (project.progress === 100) {
                    project.status = 'completed';
                }
            }
        });

        const inProgressSurveys = this.surveys.filter(s => s.status === 'in_progress');
        inProgressSurveys.forEach(survey => {
            if (Math.random() > 0.8) {
                survey.progress = Math.min(survey.progress + Math.floor(Math.random() * 5), 100);
                if (survey.progress === 100) {
                    survey.status = 'completed';
                }
            }
        });

        this.updateProgressBarsOnPage();
    }

    updateProgressBarsOnPage() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach((bar, index) => {
            if (this.currentPage === 'project_list' && this.projects[index]) {
                const project = this.projects[index];
                bar.style.width = `${project.progress}%`;
                bar.textContent = `${project.progress}%`;
            }
        });
    }

    updateAllStats() {
        if (this.currentPage === 'dashboard') {
            this.updateDashboardStats();
        } else if (this.currentPage === 'project_list') {
            this.renderProjectStats();
        } else if (this.currentPage === 'survey_list') {
            this.renderSurveyStats();
        }
    }

    // ユーティリティ機能
    setupStatisticsCards() {
        const statCards = document.querySelectorAll('.card[class*="border-"]');
        statCards.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                this.handleStatCardClick(card);
            });
        });
    }

    handleStatCardClick(card) {
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 150);

        // フィルターの適用
        if (card.classList.contains('border-warning')) {
            this.filterByStatus('in_progress');
        } else if (card.classList.contains('border-success')) {
            this.filterByStatus('completed');
        } else if (card.classList.contains('border-info')) {
            this.filterByStatus('survey');
        }
    }

    filterByStatus(status) {
        const statusFilter = document.getElementById('status') || document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.value = status;
            this.applyFilters();
        }
    }

    setupRealTimeFeatures() {
        // Webソケット接続のシミュレーション
        this.simulateWebSocketUpdates();
    }

    simulateWebSocketUpdates() {
        setInterval(() => {
            this.showRandomNotification();
        }, 15000);
    }

    showRandomNotification() {
        const notifications = [
            '新しい案件が登録されました',
            '調査が完了しました',
            '職人の稼働状況が更新されました',
            '見積もりが承認されました'
        ];

        const message = notifications[Math.floor(Math.random() * notifications.length)];
        this.showToast(message, 'info');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Toast containerの作成
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    // 職人関連機能
    contactCraftsman(id) {
        const craftsman = this.craftsmen.find(c => c.id === id);
        if (craftsman) {
            this.showToast(`${craftsman.name}に連絡しました (${craftsman.phone})`, 'success');
        }
    }

    assignCraftsman(id) {
        const craftsman = this.craftsmen.find(c => c.id === id);
        if (craftsman) {
            if (craftsman.status === '稼働中') {
                this.showToast(`${craftsman.name}は現在稼働中です`, 'warning');
            } else {
                craftsman.status = '稼働中';
                this.showToast(`${craftsman.name}をアサインしました`, 'success');
                this.renderCraftsmanTable();
            }
        }
    }

    startDashboardUpdates() {
        setInterval(() => {
            this.animateNumbers();
        }, 8000);
    }

    animateNumbers() {
        const numberElements = document.querySelectorAll('.card h3');
        numberElements.forEach(element => {
            const finalNumber = parseInt(element.textContent);
            let currentNumber = 0;
            const increment = Math.ceil(finalNumber / 20);

            const timer = setInterval(() => {
                currentNumber += increment;
                if (currentNumber >= finalNumber) {
                    currentNumber = finalNumber;
                    clearInterval(timer);
                }
                element.textContent = currentNumber;
            }, 50);
        });
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ConstructionSaaS();

    // CSS追加スタイル
    const additionalStyles = `
        .avatar-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .rating .fas, .rating .far {
            font-size: 0.875rem;
        }

        .toast-container {
            z-index: 1050;
        }

        .card {
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .progress-bar {
            transition: width 0.6s ease;
        }

        .table tbody tr {
            transition: background-color 0.2s ease;
        }

        .table tbody tr:hover {
            background-color: rgba(0, 123, 255, 0.05);
        }

        .btn-group .btn {
            transition: all 0.2s ease;
        }

        .btn-group .btn:hover {
            transform: translateY(-1px);
        }

        .survey-card {
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .survey-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .fade-in {
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-number {
            transition: all 0.5s ease;
        }

        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);

    // 完全役職管理機能（労働者派遣法準拠）
    window.userRole = localStorage.getItem('userRole') || 'employee'; // 'employee' or 'temporary'

    window.toggleRole = function() {
        const oldRole = window.userRole;
        window.userRole = window.userRole === 'employee' ? 'temporary' : 'employee';
        localStorage.setItem('userRole', window.userRole);

        // 役職変更の監査ログ
        if (window.app) {
            window.app.logAuditEvent('ROLE_CHANGED', {
                oldRole: oldRole,
                newRole: window.userRole,
                changedBy: 'user_toggle',
                timestamp: new Date().toISOString(),
                complianceNote: '労働者派遣法第23条準拠'
            });
        }

        updateDashboardForRole();

        // 役職変更後のページリロード（完全分離のため）
        setTimeout(() => {
            if (window.userRole === 'employee') {
                window.location.href = 'index_manager.html';
            } else {
                window.location.href = 'index_staff.html';
            }
        }, 500);
    };

    function updateDashboardForRole() {
        const currentRoleElement = document.getElementById('currentRole');
        const employeeActions = document.getElementById('employeeActions');
        const temporaryActions = document.getElementById('temporaryActions');
        const employeeStats = document.getElementById('employeeStats');
        const temporaryStats = document.getElementById('temporaryStats');
        const employeeProjects = document.getElementById('employeeProjects');
        const temporaryProjects = document.getElementById('temporaryProjects');

        if (currentRoleElement) {
            currentRoleElement.textContent = window.userRole === 'employee' ? '社員' : '派遣スタッフ';
            currentRoleElement.className = `fw-bold text-${window.userRole === 'employee' ? 'primary' : 'success'}`;
        }

        // アクションの切り替え
        if (employeeActions && temporaryActions) {
            if (window.userRole === 'employee') {
                employeeActions.style.display = 'block';
                temporaryActions.style.display = 'none';
            } else {
                employeeActions.style.display = 'none';
                temporaryActions.style.display = 'block';
            }
        }

        // 統計カードの切り替え
        if (employeeStats && temporaryStats) {
            if (window.userRole === 'employee') {
                employeeStats.style.display = 'flex';
                temporaryStats.style.display = 'none';
            } else {
                employeeStats.style.display = 'none';
                temporaryStats.style.display = 'flex';
            }
        }

        // 案件表示の切り替え
        if (employeeProjects && temporaryProjects) {
            if (window.userRole === 'employee') {
                employeeProjects.style.display = 'block';
                temporaryProjects.style.display = 'none';
            } else {
                employeeProjects.style.display = 'none';
                temporaryProjects.style.display = 'block';
            }
        }

        // サイドバーナビゲーションの更新
        updateSidebarForRole();
    }

    function updateSidebarForRole() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        // ナビゲーションアイテムを役職に応じて表示/非表示
        const navItems = sidebar.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            const link = item.querySelector('a');
            if (!link) return;

            const href = link.getAttribute('href');

            if (window.userRole === 'temporary') {
                // 派遣スタッフ用：限定された機能のみ表示
                if (href.includes('index.html') ||
                    href.includes('surveys/survey_') ||
                    href.includes('contractors/contractor_coordination.html') ||
                    href.includes('contractors/contractor_notification.html')) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            } else {
                // 社員用：すべて表示
                item.style.display = 'block';
            }
        });

        // サイドバーのメニュー名も変更
        const menuHeading = sidebar.querySelector('.sidebar-heading span');
        if (menuHeading) {
            menuHeading.textContent = window.userRole === 'employee' ? 'メインメニュー' : '派遣スタッフメニュー';
        }
    }

    // 検索・フィルター機能（社員用）
    window.filterProjects = function(status) {
        const rows = document.querySelectorAll('#projectTableBody tr');

        rows.forEach(row => {
            const rowStatus = row.getAttribute('data-status');
            if (status === 'all' || rowStatus === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });

        // ボタンのアクティブ状態を更新
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    };

    window.searchProjects = function() {
        const searchTerm = document.getElementById('projectSearch').value.toLowerCase();
        const rows = document.querySelectorAll('#projectTableBody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    };

    // ページ読み込み時に役職に応じてダッシュボードを更新
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            updateDashboardForRole();
        }, 100);
    });
});