// 建築派遣SaaS - メインアプリケーション

class ConstructionSaaS {
    constructor() {
        this.projects = this.loadDemoData();
        this.surveys = this.loadSurveyData();
        this.craftsmen = this.loadCraftsmenData();
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initPageSpecificFeatures();
        this.startRealTimeUpdates();
    }

    // データローディング
    loadDemoData() {
        return [
            {
                id: 1,
                name: "新宿オフィスビル清掃",
                customer: "ABC商事株式会社",
                category: "cleaning",
                status: "in_progress",
                budget: 500000,
                progress: 60,
                created: "2025-09-10",
                location: "新宿区西新宿1-1-1"
            },
            {
                id: 2,
                name: "渋谷マンション配管工事",
                customer: "XYZ不動産",
                category: "plumbing",
                status: "survey",
                budget: 800000,
                progress: 30,
                created: "2025-09-12",
                location: "渋谷区道玄坂2-2-2"
            },
            {
                id: 3,
                name: "六本木店舗内装リフォーム",
                customer: "レストランチェーン株式会社",
                category: "interior",
                status: "completed",
                budget: 1200000,
                progress: 100,
                created: "2025-09-01",
                location: "港区六本木6-6-6"
            },
            {
                id: 4,
                name: "品川オフィス電気工事",
                customer: "テック企業A",
                category: "electrical",
                status: "scheduled",
                budget: 600000,
                progress: 10,
                created: "2025-09-14",
                location: "品川区大井1-1-1"
            },
            {
                id: 5,
                name: "池袋商業施設清掃",
                customer: "商業施設管理会社",
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
                skill: "清掃",
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
                skill: "配管",
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
                skill: "内装",
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
                skill: "電気",
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
                skill: "清掃",
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
            '清掃': 'info',
            '配管': 'primary',
            '内装': 'warning',
            '電気': 'danger'
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
});