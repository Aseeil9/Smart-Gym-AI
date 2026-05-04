const API_URL = window.location.origin;
const WS_URL = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

async function fetchAuth(endpoint, options = {}) {
    if (!options.headers) options.headers = {};
    const token = localStorage.getItem('gymToken');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(`${API_URL}${endpoint}`, options);
}

// Global state
window.GymApp = {
    currentUser: null,
    role: null,
    charts: {
        athlete: null,
        steps: null,
        comparison: null,
        sleep: null,
        coachTeam: null,
        modal: null,
        adminRevenue: null
    }
};
