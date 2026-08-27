/**
 * EnergyCalendar — Market Driven Productivity & Biohacking Suite (v1.4.0)
 * Handles Context Switch Tax, Jetlag Chrono-Protocols, Biophilic Space & Workout Timing
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

  // --- Context Switch Tax Modal ---
  async function openContextSwitchModal() {
    const modal = byId("context-switch-modal");
    if (!modal) return;
    modal.classList.remove("hidden");

    try {
      const res = await fetch("/api/v1/energy/context-switch/tax", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tasks: [
            { title: "Kódolás (Deep Work)", load_type: "deep_work", duration_minutes: 60 },
            { title: "Email & Admin", load_type: "admin", duration_minutes: 30 },
            { title: "Architektúra UI", load_type: "creative", duration_minutes: 45 },
            { title: "Számlák", load_type: "admin", duration_minutes: 20 },
            { title: "Kód refaktor", load_type: "deep_work", duration_minutes: 60 }
          ]
        })
      });
      const data = await res.json();

      const taxEl = byId("switch-tax-minutes");
      if (taxEl) taxEl.textContent = data.fragmentation_tax_minutes + " perc";

      const gainEl = byId("switch-gain-pct");
      if (gainEl) gainEl.textContent = "+" + data.optimization_gain_percent + "%";

      const advEl = byId("switch-advice-text");
      if (advEl) advEl.textContent = data.advice;

      const listEl = byId("batched-tasks-preview");
      if (listEl) {
        listEl.innerHTML = data.batched_tasks.map((t, idx) => `
          <div class="batch-preview-row">
            <span class="batch-idx">${idx + 1}.</span>
            <span class="batch-title">${esc(t.title)}</span>
            <span class="batch-load load-pill-${t.load_type}">${esc(t.load_type.toUpperCase())}</span>
          </div>
        `).join("");
      }
    } catch (e) {
      showToast("Hiba a kontextusváltási adó lekérésekor", true);
    }
  }

  // --- Jetlag & Travel Modal ---
  async function handleJetlagSubmit(e) {
    e.preventDefault();
    const orig = parseInt(byId("input-origin-utc")?.value || "1", 10);
    const targ = parseInt(byId("input-target-utc")?.value || "-5", 10);

    try {
      const res = await fetch("/api/v1/energy/jetlag/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origin_utc_offset: orig, target_utc_offset: targ })
      });
      const data = await res.json();

      const out = byId("jetlag-results-container");
      if (out) {
        out.innerHTML = `
          <div class="jetlag-summary-tag">✈️ ${esc(data.guidance)}</div>
          <div class="jetlag-protocols-list">
            ${data.protocols.map(p => `
              <div class="jetlag-day-item">
                <span class="jetlag-day-num">${p.day_number}. Nap</span>
                <div class="jetlag-day-details">
                  <div>⏰ Ébredés: <strong>${p.shifted_wake_time}</strong> | Lefekvés: <strong>${p.shifted_sleep_time}</strong></div>
                  <div class="text-cyan">☀️ ${esc(p.morning_light_action)}</div>
                  <div class="text-purple">🌙 ${esc(p.evening_melatonin_action)}</div>
                </div>
              </div>
            `).join("")}
          </div>
        `;
      }
    } catch (err) {
      showToast("Hiba a jetlag protokoll generálásakor", true);
    }
  }

  // --- Workout & Biophilic Modal ---
  async function openWorkoutModal() {
    const modal = byId("workout-modal");
    if (!modal) return;
    modal.classList.remove("hidden");

    try {
      const [wRes, bioRes] = await Promise.all([
        fetch("/api/v1/energy/workout/timing", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ wake_time: "07:00", sleep_time: "23:00", workout_type: "STRENGTH_HYPERTROPHY" })
        }),
        fetch("/api/v1/energy/biophilic/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ co2_ppm: 950, temperature_celsius: 21.8, noise_db: 48.0 })
        })
      ]);
      const wData = await wRes.json();
      const bioData = await bioRes.json();

      const wBox = byId("workout-timing-box");
      if (wBox) {
        wBox.innerHTML = `
          <div class="workout-window-highlight">🏋️ Csúcs Erőedzés Ablak: <strong>${esc(wData.optimal_window_start)} - ${esc(wData.optimal_window_end)}</strong></div>
          <p class="workout-rationale">💡 ${esc(wData.biological_rationale)}</p>
          <div class="workout-cutoff">🛑 Edzés Stop (Alvásvédelem): <strong>${esc(wData.sleep_protection_cutoff)}</strong></div>
        `;
      }

      const bioBox = byId("biophilic-audit-box");
      if (bioBox) {
        bioBox.innerHTML = `
          <div class="bio-status-badge status-${bioData.air_quality_status.toLowerCase()}">Levegőminőség: ${bioData.air_quality_status} (-${bioData.cognitive_penalty_percent}% kognitív hatás)</div>
          <ul class="bio-recs">${bioData.recommendations.map(r => `<li>${esc(r)}</li>`).join("")}</ul>
        `;
      }
    } catch (e) {
      showToast("Hiba az edzés és környezeti adatok lekérésekor", true);
    }
  }

  // Bind Events
  document.addEventListener("DOMContentLoaded", () => {
    byId("btn-open-context-tax")?.addEventListener("click", openContextSwitchModal);
    byId("btn-close-context-tax")?.addEventListener("click", () => byId("context-switch-modal")?.classList.add("hidden"));
    byId("btn-close-context-tax-btn")?.addEventListener("click", () => byId("context-switch-modal")?.classList.add("hidden"));

    byId("btn-open-jetlag")?.addEventListener("click", () => byId("jetlag-modal")?.classList.remove("hidden"));
    byId("btn-close-jetlag")?.addEventListener("click", () => byId("jetlag-modal")?.classList.add("hidden"));
    byId("jetlag-form")?.addEventListener("submit", handleJetlagSubmit);

    byId("btn-open-workout")?.addEventListener("click", openWorkoutModal);
    byId("btn-close-workout")?.addEventListener("click", () => byId("workout-modal")?.classList.add("hidden"));
    byId("btn-close-workout-btn")?.addEventListener("click", () => byId("workout-modal")?.classList.add("hidden"));
  });
})();
