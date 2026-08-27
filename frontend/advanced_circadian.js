/**
 * EnergyCalendar — Advanced Circadian Suite Frontend Controller (v1.3.0)
 * Handles Biometrics Sync, Weekly Macro-Matrix, Micro-Recovery and Analytics
 */
(function () {
  "use strict";
  const byId = (id) => document.getElementById(id);
  const esc = (s) => (s ? String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") : "");

  function showToast(msg, isWarn) {
    const c = byId("toast-container");
    if (!c) return;
    const t = document.createElement("div");
    t.className = "toast " + (isWarn ? "toast-warning" : "");
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }

  // --- 1. Biometrics Sync ---
  async function handleBiometricsSubmit(e) {
    e.preventDefault();
    const hrvEl = byId("input-hrv"), rhrEl = byId("input-rhr");
    const deepEl = byId("input-deep-sleep"), remEl = byId("input-rem-sleep");
    const hrv = parseFloat(hrvEl ? hrvEl.value : "65");
    const rhr = parseFloat(rhrEl ? rhrEl.value : "54");
    const deep = parseInt(deepEl ? deepEl.value : "75", 10);
    const rem = parseInt(remEl ? remEl.value : "85", 10);

    try {
      const res = await fetch("/api/v1/energy/biometrics/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hrv_rmssd: hrv,
          resting_hr: rhr,
          deep_sleep_minutes: deep,
          rem_sleep_minutes: rem,
          wake_time: "07:00"
        })
      });
      if (!res.ok) throw new Error("Biometrikus hiba");
      const data = await res.json();
      
      const slider = byId("sleep-quality-slider");
      const label = byId("sleep-quality-label");
      const recPct = Math.round(data.recovery_factor * 100);
      if (slider) slider.value = recPct;
      if (label) label.textContent = "Alvásminőség / Vitalitás: " + recPct + "% (Biometrikus)";
      
      byId("biometrics-modal")?.classList.add("hidden");
      showToast("⌚ " + data.message);
      
      byId("btn-reflow-now")?.click();
    } catch (err) {
      showToast("❌ Biometrikus szinkronizáció sikertelen", true);
    }
  }

  // --- 2. Weekly Macro Matrix ---
  async function openWeeklyMatrix() {
    const modal = byId("weekly-matrix-modal");
    if (!modal) return;
    modal.classList.remove("hidden");
    const container = byId("weekly-matrix-container");
    const summary = byId("weekly-summary-box");
    if (container) container.innerHTML = '<p class="loading-text">Heti cirkadián mátrix generálása...</p>';

    try {
      const res = await fetch("/api/v1/energy/weekly/matrix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: { wake_time: "07:00", sleep_time: "23:00" },
          tasks_pool: [
            { title: "Stratégiai tervezés", duration: 120, cognitive_load: "DEEP_WORK" },
            { title: "Kód refaktor", duration: 90, cognitive_load: "DEEP_WORK" },
            { title: "UI/UX vázlatok", duration: 60, cognitive_load: "CREATIVE" },
            { title: "Pénzügyek és admin", duration: 45, cognitive_load: "ADMIN" }
          ],
          start_date: new Date().toISOString().split("T")[0]
        })
      });
      if (!res.ok) throw new Error("Heti mátrix hiba");
      const data = await res.json();

      if (container) {
        container.innerHTML = data.days_schedule.map(d => `
          <div class="weekly-day-card ${d.is_focus_day ? "day-focus" : ""} ${d.is_recovery_day ? "day-recovery" : ""}">
            <div class="day-card-header">
              <span class="day-title">${esc(d.day_name)}</span>
              <span class="day-tag">${d.is_focus_day ? "🚀 Fókusz Nap" : d.is_recovery_day ? "🔋 Pihenő" : "⚖️ Egyensúly"}</span>
            </div>
            <div class="day-metrics">
              <span>🧠 Mélymunka: <strong>${d.total_deep_work_minutes}m</strong></span>
              <span>📋 Admin: <strong>${d.total_admin_minutes}m</strong></span>
            </div>
            <div class="day-task-tags">
              ${d.tasks.map(t => `<span class="task-mini-chip">${esc(t.title)}</span>`).join("")}
            </div>
          </div>
        `).join("");
      }

      if (summary) {
        summary.innerHTML = `
          <div class="weekly-score-badge">⚡ Heti Egyensúly: <strong>${data.weekly_balance_score}%</strong></div>
          <p class="weekly-rec-text">💡 ${esc(data.recommendation)}</p>
        `;
      }
    } catch (err) {
      if (container) container.innerHTML = '<p class="error-text">Nem sikerült lekérni a heti mátrixot.</p>';
    }
  }

  // --- 3. Micro-Recovery and Light Protocol ---
  async function openMicroRecoveryModal() {
    const modal = byId("micro-recovery-modal");
    if (!modal) return;
    modal.classList.remove("hidden");

    try {
      const [recRes, photoRes] = await Promise.all([
        fetch("/api/v1/energy/micro-recovery/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ continuous_screen_minutes: 80 })
        }),
        fetch("/api/v1/energy/phototherapy/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ wake_time: "06:30", sleep_time: "22:30", target_lux: 10000 })
        })
      ]);

      const recData = await recRes.json();
      const photoData = await photoRes.json();

      const sighP = byId("micro-sigh-text");
      if (sighP) sighP.textContent = recData.physiological_sigh_instructions;

      const listDiv = byId("micro-breaks-list");
      if (listDiv) {
        listDiv.innerHTML = recData.micro_breaks.map(b => `
          <div class="micro-break-item">
            <span class="micro-time">+${b.trigger_at_minute} perc</span>
            <div class="micro-action-wrap">
              <strong>${esc(b.name)} (${b.duration_seconds} mp)</strong>
              <p>${esc(b.action)}</p>
            </div>
          </div>
        `).join("");
      }

      const photoDiv = byId("phototherapy-schedule");
      if (photoDiv) {
        photoDiv.innerHTML = `
          <div class="photo-row"><span class="photo-label">🌅 Reggeli 10k Lux Napfény:</span> <strong class="text-cyan">${esc(photoData.morning_light_window)}</strong></div>
          <div class="photo-row"><span class="photo-label">☀️ Déli Cirkadián Rögzítés:</span> <strong class="text-gold">${esc(photoData.midday_sun_window)}</strong></div>
          <div class="photo-row"><span class="photo-label">🕶️ Kékfény Stop / Szemüveg:</span> <strong class="text-purple">${esc(photoData.evening_blueblocker_time)}-tól</strong></div>
        `;
      }
    } catch (err) {
      showToast("Hiba a mikroszünet protokoll betöltésekor", true);
    }
  }

  // --- 4. Analytics and Alignment ---
  async function openAnalyticsModal() {
    const modal = byId("analytics-modal");
    if (!modal) return;
    modal.classList.remove("hidden");

    try {
      const [alignRes, burnoutRes] = await Promise.all([
        fetch("/api/v1/energy/analytics/alignment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scheduled_slots: [
              { task_id: "t1", title: "Deep Work", start_time: "09:00", end_time: "11:00", duration: 120, cognitive_load: "DEEP_WORK", assigned_energy_avg: 8.8 },
              { task_id: "t2", title: "Creative", start_time: "11:30", end_time: "12:30", duration: 60, cognitive_load: "CREATIVE", assigned_energy_avg: 6.5 }
            ],
            completed_task_ids: ["t1", "t2"]
          })
        }),
        fetch("/api/v1/energy/burnout/prediction", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            daily_debts: [2.0, 5.0, 4.0, 1.0, 3.0],
            daily_recoveries: [0.95, 0.90, 0.85, 1.0, 0.90],
            streak_days: 5
          })
        })
      ]);

      const alignData = await alignRes.json();
      const burnoutData = await burnoutRes.json();

      const scoreEl = byId("analytics-alignment-score");
      if (scoreEl) scoreEl.textContent = Math.round(alignData.alignment_score) + "%";

      const grid = byId("analytics-details-grid");
      if (grid) {
        grid.innerHTML = `
          <div class="analytics-stat-card"><span class="stat-k">Fókuszarány</span><span class="stat-v text-cyan">${Math.round(alignData.deep_work_ratio * 100)}%</span></div>
          <div class="analytics-stat-card"><span class="stat-k">Kognitív ROI</span><span class="stat-v text-mint">${alignData.energy_roi_factor}x</span></div>
          <div class="analytics-stat-card"><span class="stat-k">Befejezési Ráta</span><span class="stat-v text-gold">${Math.round(alignData.completed_rate)}%</span></div>
          <div class="analytics-stat-card"><span class="stat-k">Allosztatikus Terhelés</span><span class="stat-v text-purple">${burnoutData.allostatic_load_index}</span></div>
        `;
      }

      const banner = byId("burnout-risk-banner");
      if (banner) {
        banner.innerHTML = `
          <div class="burnout-risk-tag risk-${burnoutData.risk_level.toLowerCase()}">🛡️ Kiégési Kockázat: ${burnoutData.risk_level}</div>
          <p class="burnout-rec">${esc(burnoutData.recommendation)}</p>
        `;
      }
    } catch (err) {
      showToast("Hiba az analitikai adatok lekérésekor", true);
    }
  }

  // Bind Events
  document.addEventListener("DOMContentLoaded", () => {
    byId("btn-open-biometrics")?.addEventListener("click", () => byId("biometrics-modal")?.classList.remove("hidden"));
    byId("btn-close-biometrics")?.addEventListener("click", () => byId("biometrics-modal")?.classList.add("hidden"));
    byId("btn-cancel-biometrics")?.addEventListener("click", () => byId("biometrics-modal")?.classList.add("hidden"));
    byId("biometrics-form")?.addEventListener("submit", handleBiometricsSubmit);

    byId("btn-open-weekly")?.addEventListener("click", openWeeklyMatrix);
    byId("btn-close-weekly")?.addEventListener("click", () => byId("weekly-matrix-modal")?.classList.add("hidden"));
    byId("btn-close-weekly-btn")?.addEventListener("click", () => byId("weekly-matrix-modal")?.classList.add("hidden"));

    byId("btn-open-micro-recovery")?.addEventListener("click", openMicroRecoveryModal);
    byId("btn-close-micro")?.addEventListener("click", () => byId("micro-recovery-modal")?.classList.add("hidden"));
    byId("btn-close-micro-btn")?.addEventListener("click", () => byId("micro-recovery-modal")?.classList.add("hidden"));

    byId("btn-open-analytics")?.addEventListener("click", openAnalyticsModal);
    byId("btn-close-analytics")?.addEventListener("click", () => byId("analytics-modal")?.classList.add("hidden"));
    byId("btn-close-analytics-btn")?.addEventListener("click", () => byId("analytics-modal")?.classList.add("hidden"));
  });
})();
