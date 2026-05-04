// Athlete Specific Logic
window.initAthleteDashboard = initAthleteDashboard;
function initAthleteDashboard() {
    loadAthleteHistory();
    loadDailySummary();
    loadSleepData();
    loadAvailableCoaches();
    loadTrainingPlan();
    loadAnnouncements('Athlete');
    connectWebSocket();
}

let simInterval = null;

async function sendSensorData() {
    const hr = document.getElementById('hrSlider').value;
    const steps = document.getElementById('stepsSlider').value;
    const cal = document.getElementById('calSlider').value;

    try {
        const res = await fetchAuth('/sensor-data/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ heart_rate: parseFloat(hr), steps: parseInt(steps), calories: parseFloat(cal) })
        });
        updateSummaryWidgets(Math.round(hr), parseInt(steps), Math.round(cal));
    } catch (e) {
        console.error("Sensor Data Send Error:", e);
    }
}

function toggleAutoSimulate() {
    const btn = document.getElementById('autoSimulateBtn');
    const singleBtn = document.getElementById('singleSimulateBtn');
    
    if (simInterval) {
        clearInterval(simInterval);
        simInterval = null;
        btn.innerText = "بدء المحاكاة المستمرة (التلقائية) 🔄";
        btn.style.background = "var(--neon-purple)";
        btn.style.color = "white";
        singleBtn.disabled = false;
    } else {
        btn.innerText = "إيقاف المحاكاة التلقائية 🛑";
        btn.style.background = "var(--neon-red)";
        btn.style.color = "white";
        singleBtn.disabled = true;
        
        simInterval = setInterval(() => {
            let hrSlider = document.getElementById('hrSlider');
            let stepsSlider = document.getElementById('stepsSlider');
            let calSlider = document.getElementById('calSlider');
            
            let hr = parseFloat(hrSlider.value);
            // Increase HR to simulate effort, drop it if too high
            hr += (Math.random() * 5) - 0.5; 
            if(hr > 195) hr -= (Math.random() * 10 + 5);
            if(hr < 60) hr = 60;
            
            hrSlider.value = hr;
            document.getElementById('hrValSim').innerText = Math.round(hr);
            
            stepsSlider.value = parseInt(stepsSlider.value) + Math.floor(Math.random() * 30 + 15);
            document.getElementById('stepsValSim').innerText = stepsSlider.value;
            
            calSlider.value = parseFloat(calSlider.value) + (Math.random() * 3 + 1.5);
            document.getElementById('calValSim').innerText = Math.round(calSlider.value * 10) / 10;
            
            sendSensorData();
        }, 2500); // Send data every 2.5 seconds
    }
}

function updateSummaryWidgets(hr, steps, cal) {
    const hrEl = document.getElementById('summary-hr');
    const stEl = document.getElementById('summary-steps');
    const clEl = document.getElementById('summary-cal');
    
    if(hrEl) hrEl.innerText = `${hr} BPM`;
    if(stEl) stEl.innerText = steps;
    if(clEl) clEl.innerText = cal;
    
    // Animate or change color if high
    if(hr > 120 && hrEl) hrEl.style.color = 'var(--neon-red)';
    else if(hrEl) hrEl.style.color = 'var(--text-main)';
}

// Safe stubs for missing features to prevent crashes
window.loadAthleteHistory = async function() { console.log('Athlete History Loaded'); };
window.loadDailySummary = async function() { console.log('Daily Summary Loaded'); };
window.loadSleepData = async function() { console.log('Sleep Data Loaded'); };
window.loadAvailableCoaches = async function() { console.log('Coaches Loaded'); };
window.loadTrainingPlan = async function() { console.log('Training Plan Loaded'); };
window.loadAnnouncements = async function(role) { console.log(role + ' Announcements Loaded'); };

let wsAlerts = null;
window.connectWebSocket = function() { 
    if (wsAlerts) wsAlerts.close();
    if (!window.GymApp || !window.GymApp.currentUser) return;
    
    const userId = window.GymApp.currentUser.id;
    wsAlerts = new WebSocket(`${WS_URL}/ws/alerts/${userId}`);
    
    wsAlerts.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("WS ALERT:", data);
        
        if(data.type === 'URGENT_ALERT' || data.type === 'SOS_EMERGENCY' || data.type === 'INJURY_REPORT') {
            const box = document.createElement('div');
            box.className = 'alert-box danger mt-2';
            box.innerHTML = `<strong>${data.message}</strong>`;
            
            if (window.GymApp.role === 'Athlete') {
                const container = document.getElementById('alertsContainer');
                if (container) {
                    if(container.innerHTML.includes('في انتظار')) container.innerHTML = '';
                    container.prepend(box);
                }
            } else if (window.GymApp.role === 'Coach') {
                const container = document.getElementById('team-analytics-content');
                if (container) {
                    if(container.innerHTML.includes('جاري فحص')) container.innerHTML = '';
                    container.prepend(box);
                }
            }
        } else if (data.type === 'COACH_DIRECT_MESSAGE') {
            alert(`رسالة من الكابتن ${data.coach_name}:\n${data.message}`);
        }
    };
    
    wsAlerts.onclose = function() {
        setTimeout(window.connectWebSocket, 5000);
    };
};

// Map HTML global onclicks
window.sendSensorData = sendSensorData;
window.toggleAutoSimulate = toggleAutoSimulate;
window.sendSOS = async function() { 
    try {
        const res = await fetchAuth('/athletes/emergency/', { method: 'POST' });
        if(res.ok) alert('🚨 تم إرسال نداء الطوارئ للمدربين!');
    } catch(e) { console.error(e); }
};
window.saveAthleteProfile = async function() { 
    const days = parseInt(document.getElementById('training-days-input').value);
    const hasInjury = document.querySelector('input[name="injury-radio"]:checked').value === 'yes';
    const injuryDetails = document.getElementById('injury-details-input').value;
    
    try {
        await fetchAuth('/users/me/profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ training_days: days, has_injury: hasInjury, injury_details: injuryDetails })
        });
        
        const planRes = await fetchAuth('/users/me/generate-training-plan', { method: 'POST' });
        if (planRes.ok) {
            const planData = await planRes.json();
            document.getElementById('ai-plan-container').innerText = planData.ai_generated_plan;
            alert('تم تحديث الملف وتوليد الخطة بنجاح');
        }
    } catch(e) { console.error(e); }
};
window.logExerciseWeight = async function() { 
    const name = document.getElementById('exercise-name-input').value;
    const weight = parseFloat(document.getElementById('exercise-weight-input').value);
    if (!weight) return alert('الرجاء إدخال الوزن');
    try {
        const res = await fetchAuth('/users/me/log-exercise', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ exercise_name: name, muscle_group: "عام", max_weight: weight })
        });
        if(res.ok) alert('تم تسجيل الوزن الجديد!');
    } catch(e) { console.error(e); }
};
window.getSmartWeightRecommendation = async function() { 
    const name = document.getElementById('exercise-name-input').value;
    try {
        const res = await fetchAuth(`/users/me/smart-recommendation/${encodeURIComponent(name)}`);
        if(res.ok) {
            const data = await res.json();
            const box = document.getElementById('weight-recommendation-box');
            if(box){ box.style.display='block'; box.innerText = data.recommendation; }
        }
    } catch(e) { console.error(e); }
};
window.saveSleepData = async function() { 
    const hours = parseFloat(document.getElementById('sleepHoursSlider').value);
    try {
        await fetchAuth('/users/me/sleep/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ sleep_hours: hours, quality_score: 80 })
        });
        const recRes = await fetchAuth('/users/me/sleep-recommendation/');
        if (recRes.ok) {
            const recData = await recRes.json();
            const box = document.getElementById('sleep-ai-recommendation');
            if(box){ box.style.display='block'; box.innerText = recData.recommendation; }
        }
    } catch(e) { console.error(e); }
};
window.toggleInjuryDetails = function(show) {
    const el = document.getElementById('injury-details-group');
    if(el) el.style.display = show ? 'block' : 'none';
};
