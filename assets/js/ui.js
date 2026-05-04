// UI State Management
const UI = {
    views: {
        portal: null,
        login: null,
        dashboard: null
    },
    
    init() {
        console.log("UI Initializing...");
        this.views.portal = document.getElementById('view-portal');
        this.views.login = document.getElementById('view-login');
        this.views.dashboard = document.getElementById('dashboard-layout');
        
        this.setupEventListeners();
        applyLanguage();
        if (window.lucide) lucide.createIcons();
    },
    
    setupEventListeners() {
        // Portal Cards
        document.querySelectorAll('.portal-card').forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', (e) => {
                const role = card.querySelector('h3').getAttribute('data-i18n').split('-')[1];
                // Map role properly
                const roleMap = { 'athlete': 'Athlete', 'coach': 'Coach', 'admin': 'Admin' };
                UI.showLogin(roleMap[role] || 'Athlete');
            });
        });
    },
    
    hideAll() {
        Object.values(this.views).forEach(v => { if(v) v.style.display = 'none'; });
    },
    
    showLogin(role) {
        window.GymApp.role = role;
        this.hideAll();
        if(this.views.login) this.views.login.style.display = 'flex';
        
        const arRoleMap = { 'Athlete': 'المشترك', 'Coach': 'المدرب', 'Admin': 'الإدارة' };
        const sub = document.getElementById('login-subtitle');
        if(sub) sub.innerText = `تسجيل الدخول لبوابة ${arRoleMap[role]}`;
    },
    
    backToPortal() {
        this.hideAll();
        if(this.views.portal) this.views.portal.style.display = 'block';
    },

    switchTab(tabId) {
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const target = document.getElementById(tabId);
        if (target) target.classList.add('active');

        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        const link = document.querySelector(`[onclick*="${tabId}"]`);
        if (link) link.classList.add('active');
        
        if (window.lucide) lucide.createIcons();
    }
};

// Expose UI functions globally so inline HTML onclick handlers work
window.showLogin = (role) => UI.showLogin(role);
window.backToPortal = () => UI.backToPortal();
window.switchTab = (tabId) => UI.switchTab(tabId);

document.addEventListener('DOMContentLoaded', () => UI.init());
