/**
 * Energia-Ritmus & Heti Rutin-Koreografus — Circadian Productivity Suite App (SPEC-004)
 */
(function () {
  "use strict";
  const TL_START = 360, TL_END = 1380, TL_SPAN = 1020;
  const PRESETS = {
    standard: { wake_time: "07:00", sleep_time: "23:00", peak_hours: [{ start: "09:00", end: "11:30" }, { start: "16:30", end: "18:30" }], dip_hours: [{ start: "13:30", end: "15:00" }] },
    lark: { wake_time: "06:00", sleep_time: "22:00", peak_hours: [{ start: "07:30", end: "10:00" }, { start: "15:00", end: "17:00" }], dip_hours: [{ start: "12:30", end: "14:00" }] },
    "night-owl": { wake_time: "09:00", sleep_time: "23:59", peak_hours: [{ start: "11:00", end: "13:30" }, { start: "18:00", end: "21:00" }], dip_hours: [{ start: "15:00", end: "16:30" }] }
  };
  const state = {
    profile: JSON.parse(JSON.stringify(PRESETS.standard)), sleepQuality: 1.0, showCaffeineWindow: true, caffeineWindow: null,
    tasks: [
      { id: "task-1", title: "Kódolás: új auth modul 90 perc", duration_minutes: 90, load_type: "deep_work", energy_cost: 8.5, is_fixed: false },
      { id: "task-2", title: "Architektúra UI vázlat 60 perc", duration_minutes: 60, load_type: "creative", energy_cost: 6.0, is_fixed: false },
      { id: "task-3", title: "Email és számlák 45 perc", duration_minutes: 45, load_type: "admin", energy_cost: 3.0, is_fixed: false },
      { id: "task-4", title: "Délutáni kód refaktor 60 perc", duration_minutes: 60, load_type: "deep_work", energy_cost: 8.5, is_fixed: false },
      { id: "task-5", title: "Kávészünet és séta 20 perc", duration_minutes: 20, load_type: "recovery", energy_cost: -3.0, is_fixed: false }
    ],
    scheduledTasks: [], debtReport: null, energyCurve: [], zenActiveTask: null, zenTimer: null, zenSeconds: 0,
    audioCtx: null, audioNodes: null, isAudioPlaying: false
  };
  const byId = (id) => document.getElementById(id);
  const esc = (s) => (s ? String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") : "");
  const timeToMin = (t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; };
  const minToTime = (m) => { const n = ((m % 1440) + 1440) % 1440; return `${String(Math.floor(n / 60)).padStart(2, "0")}:${String(n % 60).padStart(2, "0")}`; };
  function showToast(msg, isWarn = false) {
    const c = byId("toast-container"); if (!c) return;
    const t = document.createElement("div"); t.className = `toast ${isWarn ? "toast-warning" : ""}`; t.textContent = msg; c.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }
  function getLoadMeta(t) {
    const m = { deep_work: { name: "Mélymunka", icon: "🧠", cls: "load-deep_work" }, creative: { name: "Kreatív", icon: "💡", cls: "load-creative" }, admin: { name: "Admin", icon: "📋", cls: "load-admin" }, recovery: { name: "Regeneráció", icon: "🔋", cls: "load-recovery" } };
    return m[t] || { name: t, icon: "📌", cls: "load-admin" };
  }
  // --- Web Audio Synth ---
  function initAudioSynth() {
    if (!state.audioCtx) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return false; state.audioCtx = new AC(); }
    if (state.audioCtx.state === "suspended") state.audioCtx.resume();
    return true;
  }
  function startZenAudio() {
    if (!initAudioSynth()) return;
    const ctx = state.audioCtx, masterGain = ctx.createGain(); masterGain.gain.setValueAtTime(0.01, ctx.currentTime); masterGain.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + 1.2); masterGain.connect(ctx.destination);
    const bufLen = ctx.sampleRate * 3, buf = ctx.createBuffer(1, bufLen, ctx.sampleRate), d = buf.getChannelData(0);
    let last = 0.0; for (let i = 0; i < bufLen; i++) { const w = Math.random() * 2 - 1; d[i] = (last + 0.02 * w) / 1.02; last = d[i]; d[i] *= 3.2; }
    const noiseNode = ctx.createBufferSource(); noiseNode.buffer = buf; noiseNode.loop = true;
    const filter = ctx.createBiquadFilter(); filter.type = "lowpass"; filter.frequency.value = 450;
    noiseNode.connect(filter); filter.connect(masterGain); noiseNode.start();
    const merger = ctx.createChannelMerger(2), oscL = ctx.createOscillator(), oscR = ctx.createOscillator(), beatGain = ctx.createGain();
    beatGain.gain.value = 0.06; oscL.type = "sine"; oscL.frequency.value = 210; oscR.type = "sine"; oscR.frequency.value = 220;
    oscL.connect(merger, 0, 0); oscR.connect(merger, 0, 1); merger.connect(beatGain); beatGain.connect(masterGain);
    oscL.start(); oscR.start(); state.audioNodes = { noiseNode, oscL, oscR, masterGain }; state.isAudioPlaying = true; updateAudioUI(true);
  }
  function stopZenAudio() {
    if (!state.audioNodes || !state.audioCtx) return;
    try {
      const { noiseNode, oscL, oscR, masterGain } = state.audioNodes; masterGain.gain.linearRampToValueAtTime(0.001, state.audioCtx.currentTime + 0.4);
      setTimeout(() => { try { noiseNode.stop(); oscL.stop(); oscR.stop(); noiseNode.disconnect(); oscL.disconnect(); oscR.disconnect(); masterGain.disconnect(); } catch (e) {} }, 500);
    } catch (e) {}
    state.audioNodes = null; state.isAudioPlaying = false; updateAudioUI(false);
  }
  function toggleZenAudio() { if (state.isAudioPlaying) stopZenAudio(); else startZenAudio(); }
  function updateAudioUI(isPlaying) {
    const btn = byId("btn-toggle-zen-audio"), status = byId("zen-audio-status");
    if (btn) btn.classList.toggle("active", isPlaying);
    if (status) { status.textContent = isPlaying ? "Aktív (Barna zaj + 10Hz Alfa)" : "Kikapcsolva"; status.style.color = isPlaying ? "var(--cyan-neon)" : "var(--text-dim)"; }
  }
  // --- Core API Handlers ---
  async function fetchCaffeineWindow() {
    try { const res = await fetch("/api/v1/energy/caffeine-window", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile: state.profile }) }); if (res.ok) state.caffeineWindow = await res.json(); } catch (e) { console.error(e); }
  }
  async function fetchEnergyCurve() {
    try { const res = await fetch("/api/v1/energy/profile/curve", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(state.profile) }); if (res.ok) { const d = await res.json(); state.energyCurve = d.points || []; renderCanvasCurve(); } } catch (e) { console.error(e); }
  }
  async function parseTaskNLP(raw) {
    try { const res = await fetch("/api/v1/energy/parse-task", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ raw_text: raw }) }); if (res.ok) return await res.json(); } catch (e) { console.error(e); }
    return { title: raw, duration_minutes: 45, load_type: "deep_work", energy_cost: 8.5 };
  }
  async function runAutoSchedule() {
    const btn = byId("btn-auto-schedule"); if (btn) btn.disabled = true;
    try {
      const res = await fetch("/api/v1/energy/schedule", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile: state.profile, tasks: state.tasks }) });
      if (res.ok) {
        const d = await res.json(); state.scheduledTasks = d.scheduled_tasks || []; state.debtReport = d.debt_report || null;
        if (d.energy_curve && d.energy_curve.length) state.energyCurve = d.energy_curve;
        await fetchCaffeineWindow(); renderTimeline(); renderBacklog(); updateDebtMeter(); updateStatsSidebar(); renderCanvasCurve(); showToast("⚡ Cirkadián koreográfia frissítve!");
      }
    } catch (e) { showToast("⚠️ Ütemezési hiba történt!", true); } finally { if (btn) btn.disabled = false; }
  }
  async function runReflowDay() {
    const btn = byId("btn-reflow-now"); if (btn) btn.disabled = true;
    const now = new Date(), curTime = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
    try {
      const res = await fetch("/api/v1/energy/schedule/reflow", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile: state.profile, current_time: curTime, pending_tasks: state.tasks, sleep_quality: state.sleepQuality }) });
      if (res.ok) {
        const d = await res.json(); state.scheduledTasks = d.scheduled_tasks || []; state.debtReport = d.debt_report || null;
        if (d.energy_curve && d.energy_curve.length) state.energyCurve = d.energy_curve; if (d.caffeine_window) state.caffeineWindow = d.caffeine_window;
        renderTimeline(); renderBacklog(); updateDebtMeter(); updateStatsSidebar(); renderCanvasCurve(); showToast(`🌊 Nap újrahangolva (${curTime}-tól)!`);
      }
    } catch (e) { showToast("⚠️ Újrahangolási hiba!", true); } finally { if (btn) btn.disabled = false; }
  }
  // --- SPEC-004: ICS Export, Import, Decompose & Shutdown ---
  async function exportICS() {
    try {
      const res = await fetch("/api/v1/energy/calendar/export-ics", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scheduled_tasks: state.scheduledTasks, calendar_name: "Cirkadián Energia Naptár" }) });
      if (res.ok) {
        const blob = await res.blob(), url = window.URL.createObjectURL(blob), a = document.createElement("a");
        a.href = url; a.download = "energy-calendar.ics"; document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url);
        showToast("📤 Naptár (.ics) letöltve!");
      } else { showToast("⚠️ Hiba exportáláskor!", true); }
    } catch (e) { showToast("⚠️ Hálózati hiba!", true); }
  }
  async function importICS(icsContent) {
    if (!icsContent || icsContent.trim().length < 10) { showToast("⚠️ Kérlek adj meg érvényes .ics szöveget!", true); return; }
    try {
      const res = await fetch("/api/v1/energy/calendar/import-ics", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ics_content: icsContent }) });
      if (res.ok) {
        const d = await res.json();
        if (d.imported_tasks && d.imported_tasks.length) {
          state.tasks.push(...d.imported_tasks); byId("ics-import-modal")?.classList.add("hidden");
          renderBacklog(); await runAutoSchedule(); showToast(`📥 ${d.imported_count} naptáresemény importálva!`);
        } else { showToast("ℹ️ Nem található importálható esemény.", true); }
      } else { showToast("⚠️ Hiba az .ics importálás során!", true); }
    } catch (e) { showToast("⚠️ Hálózati hiba importáláskor!", true); }
  }
  async function decomposeTask(task) {
    try {
      const res = await fetch("/api/v1/energy/decompose-task", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ task }) });
      if (res.ok) {
        const d = await res.json(), idx = state.tasks.findIndex((t) => t.id === task.id);
        if (idx !== -1 && d.subtasks && d.subtasks.length) {
          state.tasks.splice(idx, 1, ...d.subtasks); renderBacklog(); await runAutoSchedule();
          showToast(`⚡ '${task.title}' 3 kognitív fázisra bontva!`);
        }
      } else { showToast("⚠️ Feladatbontás sikertelen!", true); }
    } catch (e) { showToast("⚠️ Hálózati hiba!", true); }
  }
  async function openShutdownModal() {
    const modal = byId("shutdown-ritual-modal"); if (!modal) return;
    const now = new Date(), curTime = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
    const scheduledIds = new Set(state.scheduledTasks.map((s) => s.task_id));
    const pendingTasks = state.tasks.filter((t) => !scheduledIds.has(t.id)), completedTasks = state.tasks.filter((t) => scheduledIds.has(t.id));
    try {
      const res = await fetch("/api/v1/energy/shutdown/summary", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile: state.profile, completed_tasks: completedTasks, pending_tasks: pendingTasks, scheduled_slots: state.scheduledTasks, current_time: curTime }) });
      if (res.ok) {
        const d = await res.json();
        byId("shutdown-completed-count").textContent = d.completed_count;
        byId("shutdown-pending-count").textContent = d.pending_count;
        byId("shutdown-deepwork-min").textContent = `${d.total_deep_work_minutes} perc`;
        byId("shutdown-melatonin-gate").textContent = d.melatonin_gate_time;
        const countEl = byId("shutdown-countdown-text");
        if (countEl) countEl.textContent = d.minutes_until_melatonin > 0 ? `⏳ Melatonin Kapuig: ${d.minutes_until_melatonin} perc (${d.melatonin_gate_time})` : `🌙 Melatonin Kapu elérkezett (${d.melatonin_gate_time})! Pihenés javasolt.`;
        const pendingList = byId("shutdown-pending-list");
        if (pendingList) { pendingList.innerHTML = pendingTasks.length ? pendingTasks.map((t) => `<div class="shutdown-pending-item"><span>📌 ${esc(t.title)}</span><span class="shutdown-pending-dur">${t.duration_minutes}m</span></div>`).join("") : `<span style="font-size:0.75rem;color:var(--text-dim);">Minden feladat befejezve! 🎉</span>`; }
        const recList = byId("shutdown-recommendations");
        if (recList) recList.innerHTML = (d.recommendations || []).map((r) => `<li>${esc(r)}</li>`).join("");
        modal.classList.remove("hidden");
      }
    } catch (e) { showToast("⚠️ Hiba a lezárás lekérésekor!", true); }
  }
  // --- Rendering ---
  function renderCanvasCurve() {
    const cvs = byId("energy-wave-canvas"); if (!cvs || !state.energyCurve.length) return;
    const ctx = cvs.getContext("2d"), dpr = window.devicePixelRatio || 1, r = cvs.getBoundingClientRect(); if (!r.width || !r.height) return;
    cvs.width = r.width * dpr; cvs.height = r.height * dpr; ctx.scale(dpr, dpr);
    const w = r.width, h = r.height; ctx.clearRect(0, 0, w, h);
    const toX = (m) => Math.max(0, Math.min(w, ((m - TL_START) / TL_SPAN) * w)), toY = (e) => h - ((e / 10.0) * (h - 32) + 16);
    state.profile.peak_hours.forEach((p) => { ctx.fillStyle = "rgba(6, 182, 212, 0.12)"; ctx.fillRect(toX(timeToMin(p.start)), 0, toX(timeToMin(p.end)) - toX(timeToMin(p.start)), h); });
    state.profile.dip_hours.forEach((d) => { ctx.fillStyle = "rgba(245, 158, 11, 0.12)"; ctx.fillRect(toX(timeToMin(d.start)), 0, toX(timeToMin(d.end)) - toX(timeToMin(d.start)), h); });
    if (state.showCaffeineWindow && state.caffeineWindow) {
      const cx1 = toX(timeToMin(state.caffeineWindow.caffeine_start_time)), cx2 = toX(timeToMin(state.caffeineWindow.caffeine_cutoff_time));
      if (cx2 > cx1) {
        const cGrad = ctx.createLinearGradient(cx1, 0, cx2, 0); cGrad.addColorStop(0, "rgba(251, 191, 36, 0.04)"); cGrad.addColorStop(0.5, "rgba(251, 191, 36, 0.16)"); cGrad.addColorStop(1, "rgba(251, 191, 36, 0.04)");
        ctx.fillStyle = cGrad; ctx.fillRect(cx1, 0, cx2 - cx1, h);
        ctx.strokeStyle = "rgba(251, 191, 36, 0.5)"; ctx.lineWidth = 1; ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.moveTo(cx1, 0); ctx.lineTo(cx1, h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx2, 0); ctx.lineTo(cx2, h); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = "#fbbf24"; ctx.font = "600 11px Inter, sans-serif"; ctx.fillText("☕ Koffein Sáv", cx1 + 6, 16);
      }
    }
    ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
    ctx.strokeStyle = "rgba(6, 182, 212, 0.35)"; ctx.beginPath(); ctx.moveTo(0, toY(7.5)); ctx.lineTo(w, toY(7.5)); ctx.stroke();
    ctx.strokeStyle = "rgba(245, 158, 11, 0.35)"; ctx.beginPath(); ctx.moveTo(0, toY(4.0)); ctx.lineTo(w, toY(4.0)); ctx.stroke(); ctx.setLineDash([]);
    const pts = state.energyCurve.filter((p) => p.minute_of_day >= TL_START && p.minute_of_day <= TL_END).map((p) => ({ x: toX(p.minute_of_day), y: toY(p.energy_level), lvl: p.energy_level }));
    if (pts.length < 2) return;
    ctx.beginPath(); ctx.moveTo(pts[0].x, h); ctx.lineTo(pts[0].x, pts[0].y);
    for (let i = 0; i < pts.length - 1; i++) ctx.quadraticCurveTo(pts[i].x, pts[i].y, (pts[i].x + pts[i + 1].x) / 2, (pts[i].y + pts[i + 1].y) / 2);
    ctx.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y); ctx.lineTo(pts[pts.length - 1].x, h); ctx.closePath();
    const fillG = ctx.createLinearGradient(0, 0, 0, h); fillG.addColorStop(0, "rgba(6, 182, 212, 0.28)"); fillG.addColorStop(0.6, "rgba(168, 85, 247, 0.15)"); fillG.addColorStop(1, "rgba(10, 14, 23, 0.0)");
    ctx.fillStyle = fillG; ctx.fill();
    ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 0; i < pts.length - 1; i++) ctx.quadraticCurveTo(pts[i].x, pts[i].y, (pts[i].x + pts[i + 1].x) / 2, (pts[i].y + pts[i + 1].y) / 2);
    ctx.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y);
    const strokeG = ctx.createLinearGradient(0, 0, w, 0); pts.forEach((pt) => strokeG.addColorStop(Math.max(0, Math.min(1, pt.x / w)), pt.lvl >= 7.5 ? "#22d3ee" : (pt.lvl <= 4.0 ? "#fbbf24" : "#c084fc")));
    ctx.strokeStyle = strokeG; ctx.lineWidth = 3; ctx.stroke();
  }
  function renderTimelineMarkers() {
    const c = byId("timeline-time-markers"); if (!c) return;
    c.innerHTML = "";
    for (let m = TL_START; m <= TL_END; m += 60) {
      const el = document.createElement("div"), isP = state.profile.peak_hours.some((p) => timeToMin(p.start) <= m && m <= timeToMin(p.end)), isD = state.profile.dip_hours.some((d) => timeToMin(d.start) <= m && m <= timeToMin(d.end));
      el.className = `marker-hour ${isP ? "peak" : ""} ${isD ? "dip" : ""}`; el.textContent = minToTime(m); c.appendChild(el);
    }
  }
  function renderTimeline() {
    const c = byId("tasks-timeline"); if (!c) return;
    c.innerHTML = "";
    state.scheduledTasks.forEach((s) => {
      const sM = timeToMin(s.start_time), eM = timeToMin(s.end_time); if (eM <= TL_START || sM >= TL_END) return;
      const left = ((Math.max(TL_START, sM) - TL_START) / TL_SPAN) * 100, width = Math.max(2.5, ((Math.min(TL_END, eM) - Math.max(TL_START, sM)) / TL_SPAN) * 100);
      const meta = getLoadMeta(s.load_type), card = document.createElement("div");
      card.className = `timeline-slot-task ${meta.cls} ${s.is_auto_recovery ? "slot-auto-recovery" : ""}`;
      card.style.left = `${left.toFixed(2)}%`; card.style.width = `${width.toFixed(2)}%`; card.title = `Zen Fókusz: ${s.title}`;
      card.innerHTML = `<div class="slot-time">${esc(s.start_time)} - ${esc(s.end_time)}</div><div class="slot-title">${meta.icon} ${esc(s.title)}</div><div class="slot-meta"><span>${meta.name}</span><span class="slot-energy-badge">⚡ ${s.average_energy_level.toFixed(1)}</span></div>`;
      card.addEventListener("click", () => openZenFocus(s));
      c.appendChild(card);
    });
  }
  function renderBacklog() {
    const c = byId("task-backlog"), countBadge = byId("backlog-count"); if (!c) return;
    const scheduledIds = new Set(state.scheduledTasks.map((s) => s.task_id)), backlog = state.tasks.filter((t) => !scheduledIds.has(t.id));
    if (countBadge) countBadge.textContent = `${backlog.length} feladat`;
    c.innerHTML = "";
    if (!backlog.length) { c.innerHTML = `<span style="font-size:0.78rem;color:var(--text-dim);padding:8px;">Minden feladat ütemezve van! ✨</span>`; return; }
    backlog.forEach((t) => {
      const meta = getLoadMeta(t.load_type), cap = document.createElement("div");
      cap.className = `backlog-capsule ${meta.cls}`; cap.draggable = true;
      const decBtn = t.duration_minutes > 60 ? `<button type="button" class="btn-decompose-task" title="Kognitív bontás 3 fázisra">⚡ Bontás</button>` : "";
      cap.innerHTML = `<span class="capsule-icon">${meta.icon}</span><span class="capsule-title">${esc(t.title)}</span><span class="capsule-dur">${t.duration_minutes}m</span>${decBtn}<button type="button" class="capsule-btn-delete" title="Törlés">✕</button>`;
      cap.addEventListener("dragstart", (e) => { cap.classList.add("dragging"); e.dataTransfer.setData("text/plain", t.id); });
      cap.addEventListener("dragend", () => cap.classList.remove("dragging"));
      cap.addEventListener("click", (e) => { if (!e.target.classList.contains("capsule-btn-delete") && !e.target.classList.contains("btn-decompose-task")) openZenFocus(t); });
      const dBtn = cap.querySelector(".btn-decompose-task");
      if (dBtn) dBtn.addEventListener("click", (e) => { e.stopPropagation(); decomposeTask(t); });
      cap.querySelector(".capsule-btn-delete").addEventListener("click", (e) => { e.stopPropagation(); state.tasks = state.tasks.filter((x) => x.id !== t.id); renderBacklog(); runAutoSchedule(); });
      c.appendChild(cap);
    });
  }
  function updateDebtMeter() {
    const r = state.debtReport; if (!r) return;
    const bar = byId("meter-bar"), pctEl = byId("meter-percent"), statsEl = byId("meter-load-stats"), badge = byId("energy-debt-badge"), badgeTxt = byId("debt-badge-text");
    const pct = Math.min(100, Math.max(0, r.exhaustion_percentage));
    if (bar) { bar.style.width = `${pct}%`; bar.classList.toggle("warning", r.is_overloaded || pct > 85); }
    if (pctEl) { pctEl.textContent = `${r.exhaustion_percentage.toFixed(0)}%`; pctEl.style.color = r.is_overloaded ? "var(--crimson-neon)" : (pct > 85 ? "var(--amber-neon)" : "var(--cyan-neon)"); }
    if (statsEl) statsEl.textContent = `Kapacitás: ${r.total_capacity} | Igény: ${r.total_requested_load}`;
    if (badge && badgeTxt) {
      badge.className = r.is_overloaded ? "energy-debt-badge badge-debt" : "energy-debt-badge badge-optimal";
      badgeTxt.textContent = r.is_overloaded ? `⚠️ Adósság: +${r.energy_debt.toFixed(1)} pont` : "✓ Optimális energiamérleg";
    }
  }
  function updateStatsSidebar() {
    const r = state.debtReport;
    if (r) {
      const cap = byId("stats-capacity"), load = byId("stats-scheduled-load"), debt = byId("stats-debt"), exh = byId("stats-exhaustion"), rec = byId("recommendation-text");
      if (cap) cap.textContent = r.total_capacity.toFixed(0);
      if (load) load.textContent = r.total_requested_load.toFixed(0);
      if (debt) debt.textContent = r.energy_debt.toFixed(1);
      if (exh) exh.textContent = `${r.exhaustion_percentage.toFixed(0)}%`;
      if (rec) rec.textContent = r.recommendation;
    }
    const pEl = byId("stats-peak-hours"), dEl = byId("stats-dip-hours"), cEl = byId("stats-caffeine-window");
    if (pEl) pEl.textContent = state.profile.peak_hours.map((p) => `${p.start} - ${p.end}`).join(" & ") || "Nincs";
    if (dEl) dEl.textContent = state.profile.dip_hours.map((d) => `${d.start} - ${d.end}`).join(" & ") || "Nincs";
    if (cEl && state.caffeineWindow) cEl.textContent = `${state.caffeineWindow.caffeine_start_time} - ${state.caffeineWindow.caffeine_cutoff_time} (Cutoff: ${state.caffeineWindow.caffeine_cutoff_time})`;
  }
  // --- Zen Focus Modal Logic ---
  function openZenFocus(task) {
    const modal = byId("zen-focus-modal"); if (!modal) return;
    state.zenActiveTask = task; state.zenSeconds = (task.duration_minutes || 25) * 60;
    const titleEl = byId("zen-task-title"), loadEl = byId("zen-task-load"), energyEl = byId("zen-task-energy"), timerEl = byId("zen-timer-display");
    if (titleEl) titleEl.textContent = task.title;
    if (loadEl) loadEl.textContent = (task.load_type || "deep_work").toUpperCase();
    if (energyEl) energyEl.textContent = `⚡ ${task.energy_cost ? task.energy_cost.toFixed(1) : "5.0"}`;
    function updateTimer() { const m = Math.floor(state.zenSeconds / 60), s = state.zenSeconds % 60; if (timerEl) timerEl.textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`; }
    updateTimer(); if (state.zenTimer) clearInterval(state.zenTimer);
    state.zenTimer = setInterval(() => { if (state.zenSeconds > 0) { state.zenSeconds--; updateTimer(); } else { clearInterval(state.zenTimer); showToast("🔔 Zen Fókusz blokk véget ért!"); } }, 1000);
    modal.classList.remove("hidden");
  }
  function closeZenFocus() {
    const modal = byId("zen-focus-modal"); if (modal) modal.classList.add("hidden");
    if (state.zenTimer) clearInterval(state.zenTimer);
    stopZenAudio(); state.zenActiveTask = null;
  }
  async function completeZenTask() {
    if (state.zenActiveTask) { const id = state.zenActiveTask.task_id || state.zenActiveTask.id; state.tasks = state.tasks.filter((t) => t.id !== id); }
    closeZenFocus(); await runReflowDay(); showToast("✓ Feladat kész! A nap hátralévő része újrahangolva.");
  }
  // --- Listeners & Initialization ---
  function setupDragAndDrop() {
    const tl = byId("tasks-timeline"); if (!tl) return;
    tl.addEventListener("dragover", (e) => { e.preventDefault(); tl.classList.add("drag-over"); });
    tl.addEventListener("dragleave", () => tl.classList.remove("drag-over"));
    tl.addEventListener("drop", (e) => { e.preventDefault(); tl.classList.remove("drag-over"); showToast("📍 Feladat az idővonalra illesztve"); runAutoSchedule(); });
  }
  function setupEventListeners() {
    const input = byId("quick-task-input"), addBtn = byId("btn-add-task"), autoBtn = byId("btn-auto-schedule");
    const reflowBtn = byId("btn-reflow-now"), cafBtn = byId("btn-toggle-caffeine"), sSlider = byId("sleep-quality-slider"), sLabel = byId("sleep-quality-label");
    const expBtn = byId("btn-export-ics"), impBtn = byId("btn-import-ics"), shutBtn = byId("btn-open-shutdown");
    async function handleAdd() {
      const text = input ? input.value.trim() : ""; if (!text) return;
      const p = await parseTaskNLP(text);
      state.tasks.push({ id: `task-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, title: p.title, duration_minutes: p.duration_minutes, load_type: p.load_type, energy_cost: p.energy_cost, is_fixed: false });
      if (input) input.value = "";
      renderBacklog(); runAutoSchedule();
    }
    if (addBtn) addBtn.addEventListener("click", handleAdd);
    if (input) input.addEventListener("keydown", (e) => { if (e.key === "Enter") handleAdd(); });
    if (autoBtn) autoBtn.addEventListener("click", runAutoSchedule);
    if (reflowBtn) reflowBtn.addEventListener("click", runReflowDay);
    if (expBtn) expBtn.addEventListener("click", exportICS);
    if (shutBtn) shutBtn.addEventListener("click", openShutdownModal);
    if (cafBtn) {
      cafBtn.addEventListener("click", () => {
        state.showCaffeineWindow = !state.showCaffeineWindow; cafBtn.classList.toggle("active", state.showCaffeineWindow);
        renderCanvasCurve(); showToast(state.showCaffeineWindow ? "☕ Koffein Sáv bekapcsolva" : "Koffein Sáv elrejtve");
      });
    }
    if (sSlider) {
      sSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value, 10); state.sleepQuality = val / 100.0;
        if (sLabel) sLabel.textContent = `Alvásminőség / Vitalitás: ${val}%`;
        runReflowDay();
      });
    }
    const closeShut = byId("btn-close-shutdown"), compShut = byId("btn-complete-shutdown");
    if (closeShut) closeShut.addEventListener("click", () => byId("shutdown-ritual-modal")?.classList.add("hidden"));
    if (compShut) compShut.addEventListener("click", () => { byId("shutdown-ritual-modal")?.classList.add("hidden"); showToast("🌙 Munkanap lezárva! Jó pihenést!"); });
    const impModal = byId("ics-import-modal"), closeImp = byId("btn-close-import-modal"), cancelImp = byId("btn-cancel-import"), submitImp = byId("btn-submit-import"), fileImp = byId("ics-file-input");
    if (impBtn) impBtn.addEventListener("click", () => impModal && impModal.classList.remove("hidden"));
    if (closeImp) closeImp.addEventListener("click", () => impModal && impModal.classList.add("hidden"));
    if (cancelImp) cancelImp.addEventListener("click", () => impModal && impModal.classList.add("hidden"));
    if (fileImp) {
      fileImp.addEventListener("change", (e) => {
        const f = e.target.files && e.target.files[0];
        if (f) { const r = new FileReader(); r.onload = (ev) => { const ta = byId("ics-text-input"); if (ta) ta.value = ev.target.result; }; r.readAsText(f); }
      });
    }
    if (submitImp) submitImp.addEventListener("click", () => { const ta = byId("ics-text-input"); importICS(ta ? ta.value : ""); });
    const closeZen = byId("btn-close-zen"), compZen = byId("btn-zen-complete"), audioBtn = byId("btn-toggle-zen-audio");
    if (closeZen) closeZen.addEventListener("click", closeZenFocus);
    if (compZen) compZen.addEventListener("click", completeZenTask);
    if (audioBtn) audioBtn.addEventListener("click", toggleZenAudio);
    document.querySelectorAll(".example-chip").forEach((chip) => { chip.addEventListener("click", () => { if (input) { input.value = chip.dataset.example || ""; handleAdd(); } }); });
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.dataset.preset; if (!PRESETS[key]) return;
        document.querySelectorAll(".preset-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active"); state.profile = JSON.parse(JSON.stringify(PRESETS[key]));
        renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule();
      });
    });
    const pModal = byId("profile-modal"), form = byId("profile-form"), togglePBtn = byId("btn-toggle-profile"), closePBtn = byId("btn-close-modal"), cancelPBtn = byId("btn-cancel-modal");
    if (togglePBtn) togglePBtn.addEventListener("click", () => {
      if (!pModal) return;
      byId("input-wake-time").value = state.profile.wake_time; byId("input-sleep-time").value = state.profile.sleep_time;
      if (state.profile.peak_hours[0]) { byId("input-peak1-start").value = state.profile.peak_hours[0].start; byId("input-peak1-end").value = state.profile.peak_hours[0].end; }
      if (state.profile.peak_hours[1]) { byId("input-peak2-start").value = state.profile.peak_hours[1].start; byId("input-peak2-end").value = state.profile.peak_hours[1].end; }
      if (state.profile.dip_hours[0]) { byId("input-dip-start").value = state.profile.dip_hours[0].start; byId("input-dip-end").value = state.profile.dip_hours[0].end; }
      pModal.classList.remove("hidden");
    });
    if (closePBtn) closePBtn.addEventListener("click", () => pModal && pModal.classList.add("hidden"));
    if (cancelPBtn) cancelPBtn.addEventListener("click", () => pModal && pModal.classList.add("hidden"));
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        state.profile.wake_time = byId("input-wake-time").value; state.profile.sleep_time = byId("input-sleep-time").value;
        state.profile.peak_hours = [{ start: byId("input-peak1-start").value, end: byId("input-peak1-end").value }, { start: byId("input-peak2-start").value, end: byId("input-peak2-end").value }];
        state.profile.dip_hours = [{ start: byId("input-dip-start").value, end: byId("input-dip-end").value }];
        pModal.classList.add("hidden"); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); showToast("✓ Cirkadián profil elmentve!");
      });
    }
    window.addEventListener("resize", renderCanvasCurve);
  }
  document.addEventListener("DOMContentLoaded", async () => {
    renderTimelineMarkers(); setupDragAndDrop(); setupEventListeners();
    await fetchCaffeineWindow(); await fetchEnergyCurve(); await runAutoSchedule();
  });
})();
