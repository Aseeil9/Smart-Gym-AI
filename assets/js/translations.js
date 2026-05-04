const translations = {
    'ar': {
        // Common
        'app-title': 'Smart-Gym-Ai - البوابة الذكية',
        'portal-subtitle': 'نظام التحليل الرياضي المدعوم بالذكاء الاصطناعي',
        'role-athlete': 'بوابة المشتركين (Athletes)',
        'role-athlete-desc': 'مراقبة أدائك، خطط التدريب، وحالة الاستشفاء',
        'role-coach': 'بوابة المدربين (Coaches)',
        'role-coach-desc': 'إدارة حصص التدريب وتحليلات الفريق الحية',
        'role-admin': 'بوابة الإدارة (Admin)',
        'role-admin-desc': 'إدارة النظام، العضويات، ومقاييس الذكاء الاصطناعي',
        'login-title': 'تسجيل الدخول',
        'back-btn': 'العودة للخلف',
        'logout-btn': 'خروج',
        'lang-btn': 'English',
        'sos-btn': 'نداء طوارئ 🆘',
        'ath-stat-hr': 'آخر نبض مسجل',
        'ath-stat-steps': 'إجمالي الخطوات اليوم',
        'ath-stat-cal': 'السعرات المحروقة',
        'co-stat-active': 'المشتركين الأنشط',
        'co-stat-hr': 'متوسط النبض للفريق',
        'co-stat-steps': 'إجمالي خطوات الفريق',
        'nav-overview': 'نظرة عامة',
        'nav-training': 'خطة التمرين',
        'nav-health': 'المقاييس الصحية',
        'nav-simulator': 'المحاكي (IoT)',
        'nav-community': 'المدربين والإعلانات',
        'nav-team': 'تحليل الفريق',
        'nav-classes': 'إدارة الحصص',
        'nav-finance': 'المالية والنمو',
        'nav-users': 'المستخدمين',
        'nav-sos': 'SOS طوارئ',
        'nav-logout': 'تسجيل خروج'
    },
    'en': {
        'app-title': 'Smart-Gym-Ai - Smart Portal',
        'portal-subtitle': 'AI-Powered Sports Analytics System',
        'role-athlete': 'Athletes Portal',
        'role-athlete-desc': 'Monitor performance, training plans, and recovery',
        'role-coach': 'Coaches Portal',
        'role-coach-desc': 'Team analysis, SOS alerts, and staff control',
        'role-admin': 'Admin Portal',
        'role-admin-desc': 'Finance, memberships, and AI metrics management',
        'login-title': 'Login',
        'back-btn': 'Go Back',
        'logout-btn': 'Logout',
        'lang-btn': 'العربية',
        'sos-btn': 'Emergency SOS 🆘',
        'ath-stat-hr': 'Last Heart Rate',
        'ath-stat-steps': 'Total Steps Today',
        'ath-stat-cal': 'Calories Burned',
        'co-stat-active': 'Active Members',
        'co-stat-hr': 'Team Avg Heart Rate',
        'co-stat-steps': 'Total Team Steps',
        'nav-overview': 'Overview',
        'nav-training': 'Workout Plan',
        'nav-health': 'Health Metrics',
        'nav-simulator': 'Simulator (IoT)',
        'nav-community': 'Coaches & News',
        'nav-team': 'Team Analysis',
        'nav-classes': 'Class Mgmt',
        'nav-finance': 'Finance & Growth',
        'nav-users': 'User Management',
        'nav-sos': 'Emergency SOS',
        'nav-logout': 'Logout'
    }
};

let currentLanguage = localStorage.getItem('gymLang') || 'ar';

function applyLanguage() {
    const t = translations[currentLanguage];
    document.getElementById('html-root').setAttribute('lang', currentLanguage);
    document.getElementById('html-root').setAttribute('dir', currentLanguage === 'ar' ? 'rtl' : 'ltr');
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t && t[key]) el.innerText = t[key];
    });

    const langBtn = document.getElementById('lang-text');
    if (langBtn) langBtn.innerText = currentLanguage === 'ar' ? 'English' : 'العربية';
}

function toggleLanguage() {
    currentLanguage = currentLanguage === 'ar' ? 'en' : 'ar';
    localStorage.setItem('gymLang', currentLanguage);
    applyLanguage();
}
