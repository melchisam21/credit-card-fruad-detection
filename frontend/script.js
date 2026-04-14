/* ═══════════════════════════════════════════════════════════════
   Fraud Shield — Frontend Logic
   ═══════════════════════════════════════════════════════════════ */

// ── Configuration ────────────────────────────────────────────────
// Change this to your deployed Render URL (no trailing slash).
// For local development, use "http://localhost:8000".
const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://YOUR-RENDER-APP.onrender.com";   // ← replace after deploying

// ── Feature list (must match the backend's features.json) ────────
const FEATURES = [
    "V1","V2","V3","V4","V5","V6","V7","V8","V9","V10",
    "V11","V12","V13","V14","V15","V16","V17","V18","V19","V20",
    "V21","V22","V23","V24","V25","V26","V27","V28","scaled_amount"
];

// ── Sample transactions ──────────────────────────────────────────
const SAMPLES = {
    legit: {
        V1: -1.3598071336738, V2: -0.0727811733098, V3: 2.53634673796914,
        V4: 1.37815522427443, V5: -0.33832077,  V6: 0.46238778,
        V7: 0.23959855,       V8: 0.09869790,   V9: 0.36378697,
        V10: 0.09079417,      V11: -0.55159953,  V12: -0.61780086,
        V13: -0.99138985,     V14: -0.31116935,  V15: 1.46817697,
        V16: -0.47040053,     V17: 0.20797124,   V18: 0.02579058,
        V19: 0.40399296,      V20: 0.25141210,   V21: -0.01830678,
        V22: 0.27783758,      V23: -0.11047391,  V24: 0.06692807,
        V25: 0.12853936,      V26: -0.18911484,  V27: 0.13355838,
        V28: -0.02105305,     scaled_amount: 149.62
    },
    fraud: {
        V1: -3.0435406239976, V2: -3.15730712090496, V3: 1.08846278958118,
        V4: 2.28864087860979, V5: 1.35978818540224,  V6: -1.06423598602252,
        V7: 0.325574266158614, V8: -0.0677936531906, V9: -0.270952836226548,
        V10: -1.83316635070447, V11: 1.43327744470476, V12: -2.45832890656951,
        V13: -2.85914079980498, V14: -3.24924747768707, V15: 0.0720328899824641,
        V16: -0.508777645715832, V17: -0.99422929955993, V18: -0.311169353699879,
        V19: 0.0, V20: 0.0, V21: 0.0, V22: 0.0, V23: 0.0,
        V24: 0.0, V25: 0.0, V26: 0.0, V27: 0.0, V28: 0.0,
        scaled_amount: 1.0
    }
};

// ── State ────────────────────────────────────────────────────────
let currentData = null;     // the feature dict that will be sent
let currentMode = "quick";  // "quick" or "advanced"

// ═══════════════════════════════════════════════════════════════
// Initialisation
// ═══════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();
    buildAdvancedFields();
    checkHealth();
    fetchMetrics();

    // Update the docs link to point at the API
    const docsLink = document.getElementById("docs-link");
    if (docsLink) docsLink.href = `${API_URL}/docs`;

    // Refresh metrics every 30 seconds
    setInterval(fetchMetrics, 30_000);
});

// ═══════════════════════════════════════════════════════════════
// Health & Metrics
// ═══════════════════════════════════════════════════════════════

async function checkHealth() {
    const badge = document.getElementById("health-badge");
    const textEl = badge.querySelector(".health-text");
    try {
        const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(5000) });
        const data = await res.json();
        if (data.status === "healthy") {
            badge.className = "health-badge online";
            textEl.textContent = "API Online";
        } else {
            badge.className = "health-badge offline";
            textEl.textContent = "Degraded";
        }
    } catch {
        badge.className = "health-badge offline";
        textEl.textContent = "API Offline";
    }
}

async function fetchMetrics() {
    try {
        const res = await fetch(`${API_URL}/metrics`, { signal: AbortSignal.timeout(5000) });
        const m = await res.json();
        document.getElementById("metric-total").textContent = m.total_predictions.toLocaleString();
        document.getElementById("metric-fraud").textContent = m.total_fraud_flagged.toLocaleString();
        document.getElementById("metric-rate").textContent = m.fraud_rate_percent.toFixed(2) + "%";
    } catch {
        // Silently ignore — metrics are non-critical
    }
}

// ═══════════════════════════════════════════════════════════════
// Mode switching
// ═══════════════════════════════════════════════════════════════

function setMode(mode) {
    currentMode = mode;

    document.getElementById("btn-quick").classList.toggle("active", mode === "quick");
    document.getElementById("btn-advanced").classList.toggle("active", mode === "advanced");
    document.getElementById("mode-quick").classList.toggle("hidden", mode !== "quick");
    document.getElementById("mode-advanced").classList.toggle("hidden", mode !== "advanced");

    // Re-evaluate analyze button state
    updateAnalyzeBtn();
    lucide.createIcons();
}

// ═══════════════════════════════════════════════════════════════
// Quick mode — sample loading
// ═══════════════════════════════════════════════════════════════

function loadSample(type) {
    // Deselect all sample buttons, then select current
    document.querySelectorAll(".sample-btn").forEach(b => b.classList.remove("selected"));

    let data;
    if (type === "random") {
        data = generateRandom();
    } else {
        data = { ...SAMPLES[type] };
    }

    document.getElementById(`btn-${type}`).classList.add("selected");

    currentData = data;

    // Show preview
    const preview = document.getElementById("quick-preview");
    const preJson = document.getElementById("preview-json");
    preview.classList.remove("hidden");
    preJson.textContent = JSON.stringify(data, null, 2);

    updateAnalyzeBtn();
    lucide.createIcons();
}

function generateRandom() {
    const data = {};
    for (let i = 1; i <= 28; i++) {
        // PCA features typically range roughly -5 to +5
        data[`V${i}`] = parseFloat((Math.random() * 10 - 5).toFixed(6));
    }
    data.scaled_amount = parseFloat((Math.random() * 500).toFixed(2));
    return data;
}

// ═══════════════════════════════════════════════════════════════
// Advanced mode — field generation
// ═══════════════════════════════════════════════════════════════

function buildAdvancedFields() {
    const container = document.getElementById("pca-fields");
    for (let i = 1; i <= 28; i++) {
        const name = `V${i}`;
        const wrapper = document.createElement("div");
        wrapper.innerHTML = `
            <label for="${name}">${name}</label>
            <input type="number" id="${name}" name="${name}" step="any" placeholder="0.0" />
        `;
        container.appendChild(wrapper);
    }

    // Listen for input changes to enable analyze button
    document.getElementById("feature-form").addEventListener("input", () => updateAnalyzeBtn());
}

function gatherAdvancedData() {
    const data = {};
    let allFilled = true;
    for (const feat of FEATURES) {
        const el = document.getElementById(feat);
        if (!el || el.value === "") { allFilled = false; continue; }
        data[feat] = parseFloat(el.value);
    }
    return allFilled ? data : null;
}

// ═══════════════════════════════════════════════════════════════
// Analyze button state
// ═══════════════════════════════════════════════════════════════

function updateAnalyzeBtn() {
    const btn = document.getElementById("btn-analyze");
    if (currentMode === "quick") {
        btn.disabled = currentData === null;
    } else {
        btn.disabled = gatherAdvancedData() === null;
    }
}

// ═══════════════════════════════════════════════════════════════
// Prediction (core)
// ═══════════════════════════════════════════════════════════════

async function analyze() {
    const btn = document.getElementById("btn-analyze");
    const btnContent = btn.querySelector(".btn-content");
    const btnLoading = btn.querySelector(".btn-loading");

    // Gather data based on mode
    let data;
    if (currentMode === "quick") {
        data = currentData;
    } else {
        data = gatherAdvancedData();
    }

    if (!data) return;

    // UI: loading state
    btn.disabled = true;
    btnContent.classList.add("hidden");
    btnLoading.classList.remove("hidden");

    const startTime = performance.now();

    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
            signal: AbortSignal.timeout(15000)
        });

        const elapsed = Math.round(performance.now() - startTime);

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const result = await res.json();
        showResult(result, elapsed);
        fetchMetrics();     // refresh dashboard

    } catch (err) {
        showError(err.message);
    } finally {
        // Reset button
        btn.disabled = false;
        btnContent.classList.remove("hidden");
        btnLoading.classList.add("hidden");
    }
}

// ═══════════════════════════════════════════════════════════════
// Result display
// ═══════════════════════════════════════════════════════════════

function showResult(result, elapsedMs) {
    const section = document.getElementById("result-section");
    const card    = document.getElementById("result-card");
    const isFraud = result.fraud;
    const prob    = result.probability;

    // Card class
    card.className = `result-card glass-card ${isFraud ? "danger" : "safe"}`;

    // Verdict icon
    const iconEl = document.getElementById("verdict-icon");
    iconEl.innerHTML = isFraud
        ? '<i data-lucide="shield-alert"></i>'
        : '<i data-lucide="shield-check"></i>';

    // Verdict text
    document.getElementById("verdict-text").textContent = isFraud
        ? "Fraud Detected"
        : "Transaction Legitimate";

    document.getElementById("verdict-desc").textContent = isFraud
        ? "This transaction has been flagged as potentially fraudulent."
        : "This transaction appears to be legitimate and safe.";

    // Probability gauge
    const pct = Math.round(prob * 100);
    document.getElementById("gauge-fill").style.width = `${pct}%`;
    document.getElementById("prob-value").textContent = (prob * 100).toFixed(2) + "%";

    // Threshold marker
    const thresholdPct = result.threshold_used * 100;
    document.getElementById("gauge-threshold").style.left = `${thresholdPct}%`;
    document.getElementById("threshold-info").textContent = `Threshold: ${result.threshold_used}`;

    // Risk level
    const riskBadge = document.getElementById("risk-badge");
    const riskText  = document.getElementById("risk-text");
    let riskLevel;
    if (prob < 0.3) {
        riskLevel = "low";
        riskText.textContent = "Low Risk";
    } else if (prob < 0.7) {
        riskLevel = "medium";
        riskText.textContent = "Medium Risk";
    } else {
        riskLevel = "high";
        riskText.textContent = "High Risk";
    }
    riskBadge.className = `risk-badge ${riskLevel}`;

    // Response time
    document.getElementById("response-time").innerHTML =
        `<i data-lucide="timer"></i> ${elapsedMs}ms`;

    // Show the section
    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "nearest" });

    lucide.createIcons();
}

function showError(message) {
    const section = document.getElementById("result-section");
    const card    = document.getElementById("result-card");

    card.className = "result-card glass-card danger";
    document.getElementById("verdict-icon").innerHTML = '<i data-lucide="alert-circle"></i>';
    document.getElementById("verdict-text").textContent = "Request Failed";
    document.getElementById("verdict-desc").textContent = message;
    document.getElementById("gauge-fill").style.width = "0%";
    document.getElementById("prob-value").textContent = "—";
    document.getElementById("risk-badge").className = "risk-badge";
    document.getElementById("risk-text").textContent = "Error";
    document.getElementById("response-time").innerHTML = '<i data-lucide="timer"></i> —';
    document.getElementById("threshold-info").textContent = "";

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    lucide.createIcons();
}

// ═══════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════

function copyFeatures() {
    const text = document.getElementById("preview-json").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector(".copy-btn");
        const orig = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check"></i>';
        lucide.createIcons();
        setTimeout(() => { btn.innerHTML = orig; lucide.createIcons(); }, 1500);
    });
}
