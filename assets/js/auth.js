async function performLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorBox = document.getElementById('login-error');
    if(errorBox) errorBox.innerText = '';

    if (!email || !password) {
        if(errorBox) errorBox.innerText = 'الرجاء إدخال البيانات';
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const res = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('gymToken', data.access_token);
            loadProfileAndDashboard();
        } else {
            const errData = await res.json();
            if(errorBox) {
                errorBox.style.color = "var(--neon-red)";
                errorBox.innerText = errData.detail || 'بيانات الدخول غير صحيحة';
            }
        }
    } catch (e) {
        if(errorBox) errorBox.innerText = 'فشل الاتصال بالسيرفر';
    }
}

async function loadProfileAndDashboard() {
    try {
        const res = await fetchAuth('/users/me');
        if (!res.ok) throw new Error("Unauthorized");
        const user = await res.json();
        
        window.GymApp.currentUser = user;
        UI.hideAll();
        UI.views.dashboard.style.display = 'flex';
        
        document.getElementById('user-welcome-msg').innerText = `مرحباً بك، ${user.first_name || 'بطل'}`;
        
        // Role based activation from DB!
        let role = user.role || window.GymApp.role;
        // In the backend, Enum string might come as 'Athlete', 'Coach', etc.
        // Let's ensure it's safely capitalized
        if (role) {
            role = role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
        } else {
            role = 'Athlete'; // Default fallback
        }
        
        window.GymApp.role = role;
        toggleRoleDashboards(role, user);
        
    } catch (e) {
        console.error("Critical Profile Load Error:", e);
        alert("System Error during load: " + e.message);
        // Only go back to portal if it's an unauthorized error, otherwise dashboard might just be missing a function
        if (e.message === "Unauthorized") {
            UI.backToPortal();
        }
    }
}

// Ensure these are globally available for HTML onclicks
window.performLogin = performLogin;
window.logout = logout;

function toggleRoleDashboards(role, user) {
    // Hide all
    ['athlete', 'coach', 'admin'].forEach(r => {
        document.getElementById(`${r}-dashboard`).style.display = 'none';
        document.getElementById(`nav-${r}`).style.display = 'none';
    });

    const activeD = document.getElementById(`${role.toLowerCase()}-dashboard`);
    const activeN = document.getElementById(`nav-${role.toLowerCase()}`);
    
    if(activeD) activeD.style.display = 'block';
    if(activeN) activeN.style.display = 'block';
    
    if(role === 'Athlete') {
        document.getElementById('sos-btn').style.display = 'block';
        UI.switchTab('ath-summary');
        initAthleteDashboard();
    } else if(role === 'Coach') {
        UI.switchTab('co-overview');
        initCoachDashboard();
    } else if(role === 'Admin') {
        UI.switchTab('ad-finance');
        initAdminDashboard();
    }
}

function logout() {
    localStorage.removeItem('gymToken');
    window.location.reload();
}
