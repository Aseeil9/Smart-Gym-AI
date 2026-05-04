// Coach Module
function initCoachDashboard() {
    console.log("Coach Dashboard Loaded");
    loadCoachDashboard();
    loadCoachTeam();
    loadTeamAnalytics();
    connectWebSocket();
    loadAnnouncements('Coach');
}

async function loadCoachDashboard() {
    try {
        const res = await fetchAuth('/coach/team-analytics/');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('coach-active-count').innerText = data.stats.active_now;
            document.getElementById('coach-avg-hr').innerText = data.stats.avg_hr;
            document.getElementById('coach-total-steps').innerText = data.stats.total_steps;
            
            const container = document.getElementById('team-analytics-content');
            if(container) {
                if (data.critical_cases.length > 0) {
                    container.innerHTML = data.critical_cases.map(c => 
                        `<div class="alert-box danger mb-2"><strong>${c.athlete_name} (${c.risk}%):</strong> ${c.recommendation} <small>${c.time}</small></div>`
                    ).join('');
                } else {
                    container.innerHTML = '<div class="alert-box info">جميع المشتركين في حالة ممتازة حالياً.</div>';
                }
            }
        }
    } catch (e) { console.error(e); }
}

window.loadCoachTeam = async function() { 
    try {
        const res = await fetchAuth('/coach/team');
        if (res.ok) {
            const team = await res.json();
            const tbody = document.getElementById('coach-team-table-body');
            if(!tbody) return;
            tbody.innerHTML = '';
            team.forEach(a => {
                let badge = `<span class="badge badge-safe">سليم</span>`;
                if(a.status === 'Critical') badge = `<span class="badge badge-danger" style="background:#ff0055; color:white;">مجهود عالي</span>`;
                if(a.status === 'Injured') badge = `<span class="badge badge-warning" style="background:#ffb700; color:black;">مصاب</span>`;
                
                tbody.innerHTML += `
                    <tr>
                        <td><strong>#${a.id}</strong> - ${a.name}</td>
                        <td>${badge}</td>
                        <td>${a.last_visit || 'لم يزر بعد'}</td>
                        <td><button class="btn btn-sm btn-outline" onclick="openAthleteModal(${a.id})">ملف اللاعب</button></td>
                    </tr>
                `;
            });
        }
    } catch(e) {}
};
window.loadTeamAnalytics = async function() { loadCoachDashboard(); };

window.initCoachDashboard = initCoachDashboard;

window.updateCoachPublicInfo = async function() { 
    const hours = document.getElementById('coach-new-hours').value;
    const advice = document.getElementById('coach-new-advice').value;
    try {
        const res = await fetchAuth(`/coach/update-info/?working_hours=${encodeURIComponent(hours)}&daily_advice=${encodeURIComponent(advice)}`, { method: 'POST' });
        if (res.ok) alert('تم تحديث التواجد والنصائح بنجاح');
    } catch(e) { console.error(e); }
};

window.updateCoachParams = async function() { 
    const hr = parseInt(document.getElementById('coach-hr-limit').value);
    try {
        const res = await fetchAuth('/admin/coach-parameters', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ high_hr_threshold: hr })
        });
        if (res.ok) alert('تم تحديث معايير الإصابة في الذكاء الاصطناعي');
    } catch(e) { console.error(e); }
};

window.openAthleteModal = async function(id) {
    window.currentAthleteId = id;
    try {
        const res = await fetchAuth(`/coach/athlete/${id}/details`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('modal-athlete-name').innerText = data.profile.name;
            document.getElementById('modal-athlete-info').innerText = `أيام التمرين: ${data.profile.training_days || 0}`;
            const alertBox = document.getElementById('modal-injury-alert');
            if (data.profile.has_injury) {
                alertBox.style.display = 'block';
                document.getElementById('modal-injury-text').innerText = data.profile.injury_details;
            } else {
                alertBox.style.display = 'none';
            }
            
            const list = document.getElementById('modal-exercise-list');
            if (list) list.innerHTML = data.exercise_logs.map(l => `<li>${l.exercise_name}: ${l.max_weight}kg</li>`).join('');
            
            document.getElementById('athlete-details-modal').style.display = 'flex';
        }
    } catch(e) { console.error(e); }
};

window.closeAthleteModal = function() { 
    const el = document.getElementById('athlete-details-modal');
    if(el) el.style.display = 'none';
};

window.markAthleteRecovered = async function() { 
    const athleteId = window.currentAthleteId;
    try {
        const res = await fetchAuth(`/coach/mark-recovered/${athleteId}`, { method: 'POST' });
        if (res.ok) {
            alert('تم تأكيد تعافي الرياضي');
            window.loadCoachTeam();
            window.closeAthleteModal();
        }
    } catch(e) { console.error(e); }
};

window.sendDirectInstruction = async function() { 
    const athleteId = window.currentAthleteId;
    const msg = document.getElementById('coach-direct-msg').value;
    if(!msg) return alert('اكتب الرسالة أولاً');
    try {
        const res = await fetchAuth('/coach/send-instruction', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ athlete_id: athleteId, message: msg })
        });
        if (res.ok) {
            alert('تم إرسال التعليمات للمشترك بنجاح!');
            document.getElementById('coach-direct-msg').value = '';
            window.closeAthleteModal();
        }
    } catch(e) { console.error(e); }
};
