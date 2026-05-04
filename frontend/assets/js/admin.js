// Admin Module
window.initAdminDashboard = initAdminDashboard;
function initAdminDashboard() {
    console.log("Admin Dashboard Loaded");
    loadAdminDashboard();
    loadAdminUsers();
    initAdminCharts();
    loadSystemLogs();
}

async function loadAdminDashboard() {
    try {
        const res = await fetchAuth('/admin/dashboard-stats');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('admin-total-revenue').innerText = data.total_revenue;
            document.getElementById('admin-active-memberships').innerText = data.active_memberships;
            document.getElementById('admin-total-users').innerText = data.total_users;
            document.getElementById('admin-total-coaches').innerText = data.coaches_count;
            initAdminCharts(data.labels, data.revenue_trend);
        }
    } catch (e) { console.error(e); }
}

async function loadAdminUsers() {
    const tableBody = document.getElementById('admin-user-table-body');
    if(!tableBody) return;
    try {
        const res = await fetchAuth('/admin/users');
        if (res.ok) {
            const data = await res.json();
            tableBody.innerHTML = "";
            let athletesCount = 0;
            data.forEach(u => {
                if(u.role === 'Athlete') {
                    athletesCount++;
                    tableBody.innerHTML += `
                    <tr>
                        <td><strong>#${u.id}</strong></td>
                        <td>${u.first_name || ""} ${u.last_name || ""}</td>
                        <td>${u.email}</td>
                        <td><button class="btn btn-sm btn-outline" onclick="editAthlete(${u.id}, '${u.first_name || ''}', '${u.last_name || ''}', '${u.email}')">تعديل الملف ✏️</button></td>
                    </tr>`;
                }
            });
        }
    } catch (e) {}
}

window.createMembership = async function() {
    const userId = parseInt(document.getElementById('admin-user-id').value);
    const endDate = document.getElementById('admin-end-date').value;
    if(!userId || !endDate) return alert('الرجاء إدخال البيانات (رقم المشترك وتاريخ الانتهاء)');
    
    try {
        const res = await fetchAuth(`/memberships/?customer_id=${userId}&gym_id=1&end_date=${endDate}T23:59:59`, { method: 'POST' });
        if (res.ok) {
            alert('تم تفعيل الاشتراك للمستخدم بنجاح!');
            loadAdminDashboard();
        } else {
            const err = await res.json();
            alert('خطأ: ' + (err.detail || 'تعذر التفعيل'));
        }
    } catch(e) { console.error(e); }
};

window.editAthlete = async function(id, fname, lname, email) {
    let newFname = prompt("تعديل الاسم الأول:", fname);
    if(newFname === null) return;
    let newLname = prompt("تعديل العائلة:", lname);
    if(newLname === null) return;
    let newEmail = prompt("تعديل البريد الإلكتروني:", email);
    if(newEmail === null) return;
    
    try {
        const res = await fetchAuth(`/admin/athletes/${id}/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({first_name: newFname, last_name: newLname, email: newEmail})
        });
        if(res.ok) {
            alert('✅ تم تعديل بيانات ملف المشترك بنجاح!');
            loadAdminUsers();
        } else {
            const data = await res.json();
            alert('❌ حدث خطأ: ' + (data.detail || 'غير معروف'));
        }
    } catch(e) {
        alert('❌ خطأ في الاتصال بالسيرفر.');
    }
};

window.registerNewAthlete = async function() {
    const fname = document.getElementById('admin-new-user-fname').value;
    const lname = document.getElementById('admin-new-user-lname').value;
    const email = document.getElementById('admin-new-user-email').value;
    const pass = document.getElementById('admin-new-user-pass').value;
    const dur = document.getElementById('admin-new-user-duration').value;
    const msgBox = document.getElementById('admin-new-user-msg');
    
    msgBox.innerHTML = '';
    if(!fname || !email || !pass) {
        msgBox.innerHTML = '<span style="color:var(--neon-red)">الرجاء تعبئة الاسم والإيميل ورمز المرور</span>';
        return;
    }
    
    try {
        const res = await fetchAuth('/admin/register-athlete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                first_name: fname, last_name: lname, email: email, password: pass, duration_months: parseInt(dur)
            })
        });
        
        const data = await res.json();
        if(res.ok) {
            msgBox.innerHTML = `<span style="color:var(--neon-green)">
                تم الإنشاء! رقم المشترك الخاص به هو: <strong>${data.athlete_id}</strong><br>
                النهاية المبرمجة: ${data.end_date}
            </span>`;
            loadAdminUsers(); // Update the table
        } else {
            msgBox.innerHTML = `<span style="color:var(--neon-red)">${data.detail}</span>`;
        }
    } catch(e) {
        msgBox.innerHTML = `<span style="color:var(--neon-red)">خطأ في الاتصال بالسيرفر.</span>`;
    }
}

function initAdminCharts(labels, dataArray) {
    if(!labels) labels = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'];
    if(!dataArray) dataArray = [15000, 22000, 18000, 25000, 29000, 35000];

    // Revenue Line Chart
    const revCtx = document.getElementById('adminRevenueChart');
    if (revCtx) {
        if(window.GymApp.charts.adminRevenue) window.GymApp.charts.adminRevenue.destroy();
        window.GymApp.charts.adminRevenue = new Chart(revCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'الإيرادات الشهرية (SAR)',
                    data: dataArray,
                    borderColor: '#ffd700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // AI Overview Pie Chart
    const aiCtx = document.getElementById('adminAIStatsChart');
    if (aiCtx) {
        new Chart(aiCtx, {
            type: 'doughnut',
            data: {
                labels: ['حالة سليمة (Safe)', 'تحذير إجهاد (Warning)', 'خطر إصابة (Risk)'],
                datasets: [{
                    data: [75, 18, 7],
                    backgroundColor: ['#00ff9d', '#ffb700', '#ff0055'],
                    borderWidth: 0
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: 'white' } } }
            }
        });
    }
}

function loadSystemLogs() {
    const logsBox = document.getElementById('admin-system-logs');
    if(!logsBox) return;
    
    const sampleLogs = [
        { time: "الآن", text: "قام النظام AI بتوليد 5 خطط تدريبية جديدة.", type: "info" },
        { time: "منذ 10 د", text: "تم تسجيل اشتراك لاعب جديد بقيمة 500 ريال.", type: "success" },
        { time: "منذ 45 د", text: "تنبيه: انقطاع الاتصال بحساس المدرب (أحمد).", type: "error" },
        { time: "منذ ساعتين", text: "تم تحديث معايير الخطر في محرك ML_Engine.", type: "warning" },
        { time: "منذ 3 ساعات", text: "نسخة احتياطية لقاعدة البيانات (تمت بنجاح).", type: "success" }
    ];

    logsBox.innerHTML = sampleLogs.map(log => {
        const borderColors = {
            'info': '#00e5ff',
            'success': '#00ff9d',
            'error': '#ff0055',
            'warning': '#ffb700'
        };
        return `
        <div style="border-right: 4px solid ${borderColors[log.type]}; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;">
            <small class="text-muted">${log.time}</small>
            <div style="font-size: 0.95rem;">${log.text}</div>
        </div>
        `;
    }).join("");
}

window.saveMaintenanceNote = async function(deviceId) {
    const noteInput = document.getElementById(`note-${deviceId}`);
    const noteText = noteInput ? noteInput.value : '';
    
    // In a real scenario, this sends a POST to the backend API.
    console.log(`Saving Note for ${deviceId}: ${noteText}`);
    alert(`تم حفظ التحديث الخاص بالجهاز: ${deviceId}\nالملاحظة: ${noteText}`);
};
