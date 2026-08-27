/**
 * Energia-Ritmus & Heti Rutin-Koreografus - Interactive Circadian Productivity Suite (v1.6.0)
 * Enhanced with Time Machine HUD, Laser Scan, and Neuro-Chime Web Audio
 */
(function () {
  "use strict";
  const TL_START = 360, TL_END = 1380, TL_SPAN = 1020; // 06:00 - 23:00
  const PRESETS = {
    standard: { wake_time: "07:00", sleep_time: "23:00", peak_hours: [{ start: "09:00", end: "11:30" }, { start: "16:30", end: "18:30" }], dip_hours: [{ start: "13:30", end: "15:00" }] },
    lark: { wake_time: "06:00", sleep_time: "22:00", peak_hours: [{ start: "07:30", end: "10:00" }, { start: "15:00", end: "17:00" }], dip_hours: [{ start: "12:30", end: "14:00" }] },
    "night-owl": { wake_time: "09:00", sleep_time: "23:59", peak_hours: [{ start: "11:00", end: "13:30" }, { start: "18:00", end: "21:00" }], dip_hours: [{ start: "15:00", end: "16:30" }] }
  };

  const state = {
    profile: JSON.parse(JSON.stringify(PRESETS.standard)),
    sleepQuality: 1.0,
    showCaffeineWindow: true,
    caffeineWindow: null,
    tasks: [
      { id: "task-1", title: "Kódolás: új auth modul 90 perc", duration_minutes: 90, load_type: "deep_work", energy_cost: 8.5, is_fixed: false },
      { id: "task-2", title: "Architektúra UI vázlat 60 perc", duration_minutes: 60, load_type: "creative", energy_cost: 6.0, is_fixed: false },
      { id: "task-3", title: "Email és számlák 45 perc", duration_minutes: 45, load_type: "admin", energy_cost: 3.0, is_fixed: false },
      { id: "task-4", title: "Délutáni kód refaktor 60 perc", duration_minutes: 60, load_type: "deep_work", energy_cost: 8.5, is_fixed: false },
      { id: "task-5", title: "Kávészünet és séta 20 perc", duration_minutes: 20, load_type: "recovery", energy_cost: -3.0, is_fixed: false }
    ],
    scheduledTasks: [],
    debtReport: null,
    energyCurve: [],
    zenActiveTask: null,
    zenTimer: null,
    zenSeconds: 0,
    audioCtx: null,
    audioNodes: null,
    isAudioPlaying: false,
    draggedTaskId: null,
    // Time Machine Simulation State
    simCurrentMinute: 570, // 09:30 default
    simIsPlaying: false,
    simSpeed: 5, // 1x, 5x, 15x
    simTimer: null,
    chimeEnabled: true,
    lastChimedZone: null
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
    const m = {
      deep_work: { name: "Mélymunka", icon: "🧠", cls: "load-deep_work" },
      creative: { name: "Kreatív", icon: "💡", cls: "load-creative" },
      admin: { name: "Admin", icon: "📋", cls: "load-admin" },
      recovery: { name: "Regeneráció", icon: "🔋", cls: "load-recovery" }
    };
    return m[t] || { name: t, icon: "📌", cls: "load-admin" };
  }

  // --- Audio Neuro-Chime & Synthesizer ---
  function initAudioSynth() {
    if (!state.audioCtx) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return false; state.audioCtx = new AC(); }
    if (state.audioCtx.state === "suspended") state.audioCtx.resume();
    return true;
  }

  function playNeuroChime(freq = 528, dur = 0.8) {
    if (!state.chimeEnabled || !initAudioSynth()) return;
    try {
      const ctx = state.audioCtx;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(freq * 1.5, ctx.currentTime + dur * 0.5);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + dur);
    } catch (e) {}
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

  // --- API Handlers ---
  async function fetchCaffeineWindow() {
    try { const res = await fetch("/api/v1/energy/caffeine-window", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile: state.profile }) }); if (res.ok) state.caffeineWindow = await res.json(); } catch (e) { console.error(e); }
  }
  async function fetchEnergyCurve() {
    try { const res = await fetch("/api/v1/energy/profile/curve", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(state.profile) }); if (res.ok) { const d = await res.json(); state.energyCurve = d.points || []; renderCanvasCurve(); updateTelemetryHub(); } } catch (e) { console.error(e); }
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
        await fetchCaffeineWindow(); renderTimeline(); renderBacklog(); updateDebtMeter(); updateStatsSidebar(); updateTelemetryHub(); renderCanvasCurve();
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
        renderTimeline(); renderBacklog(); updateDebtMeter(); updateStatsSidebar(); updateTelemetryHub(); renderCanvasCurve(); showToast(`🌊 Nap újrahangolva (${curTime}-tól)!`);
      }
    } catch (e) { showToast("⚠️ Újrahangolási hiba!", true); } finally { if (btn) btn.disabled = false; }
  }

  // --- Rendering Functions ---
  function renderCanvasCurve() {
    const cvs = byId("energy-wave-canvas"); if (!cvs || !state.energyCurve.length) return;
    const ctx = cvs.getContext("2d"), dpr = window.devicePixelRatio || 1, r = cvs.getBoundingClientRect(); if (!r.width || !r.height) return;
    cvs.width = r.width * dpr; cvs.height = r.height * dpr; ctx.scale(dpr, dpr);
    const w = r.width, h = r.height; ctx.clearRect(0, 0, w, h);
    const toX = (m) => Math.max(0, Math.min(w, ((m - TL_START) / TL_SPAN) * w)), toY = (e) => h - ((e / 10.0) * (h - 36) + 18);

    // 1. Shaded Focus & Dip Bands
    state.profile.peak_hours.forEach((p, idx) => {
      const x1 = toX(timeToMin(p.start)), x2 = toX(timeToMin(p.end));
      const pGrad = ctx.createLinearGradient(x1, 0, x2, 0);
      pGrad.addColorStop(0, "rgba(0, 240, 255, 0.08)"); pGrad.addColorStop(0.5, "rgba(0, 240, 255, 0.22)"); pGrad.addColorStop(1, "rgba(0, 240, 255, 0.08)");
      ctx.fillStyle = pGrad; ctx.fillRect(x1, 0, x2 - x1, h);
      ctx.fillStyle = "rgba(0, 240, 255, 0.85)"; ctx.font = "700 10px 'Space Grotesk', sans-serif";
      ctx.fillText(`🚀 CSÚCS ${idx + 1}`, x1 + 6, 18);
    });

    state.profile.dip_hours.forEach((d) => {
      const x1 = toX(timeToMin(d.start)), x2 = toX(timeToMin(d.end));
      const dGrad = ctx.createLinearGradient(x1, 0, x2, 0);
      dGrad.addColorStop(0, "rgba(255, 183, 3, 0.05)"); dGrad.addColorStop(0.5, "rgba(255, 183, 3, 0.18)"); dGrad.addColorStop(1, "rgba(255, 183, 3, 0.05)");
      ctx.fillStyle = dGrad; ctx.fillRect(x1, 0, x2 - x1, h);
      ctx.fillStyle = "rgba(255, 183, 3, 0.85)"; ctx.font = "700 10px 'Space Grotesk', sans-serif";
      ctx.fillText("🍲 MÉLYPONT (DIP)", x1 + 6, 18);
    });

    // 2. Caffeine Band
    if (state.showCaffeineWindow && state.caffeineWindow) {
      const cx1 = toX(timeToMin(state.caffeineWindow.caffeine_start_time)), cx2 = toX(timeToMin(state.caffeineWindow.caffeine_cutoff_time));
      if (cx2 > cx1) {
        const cGrad = ctx.createLinearGradient(cx1, 0, cx2, 0); cGrad.addColorStop(0, "rgba(255, 209, 102, 0.04)"); cGrad.addColorStop(0.5, "rgba(255, 209, 102, 0.16)"); cGrad.addColorStop(1, "rgba(255, 209, 102, 0.04)");
        ctx.fillStyle = cGrad; ctx.fillRect(cx1, 0, cx2 - cx1, h);
        ctx.strokeStyle = "rgba(255, 209, 102, 0.6)"; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
        ctx.beginPath(); ctx.moveTo(cx1, 0); ctx.lineTo(cx1, h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx2, 0); ctx.lineTo(cx2, h); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = "#ffd166"; ctx.font = "700 10px 'Space Grotesk', sans-serif"; ctx.fillText("☕ KOFFEIN SÁV", cx1 + 6, 32);
      }
    }

    // 3. Grid Lines
    ctx.setLineDash([4, 6]); ctx.lineWidth = 1;
    ctx.strokeStyle = "rgba(0, 240, 255, 0.3)"; ctx.beginPath(); ctx.moveTo(0, toY(7.5)); ctx.lineTo(w, toY(7.5)); ctx.stroke();
    ctx.strokeStyle = "rgba(255, 183, 3, 0.3)"; ctx.beginPath(); ctx.moveTo(0, toY(4.0)); ctx.lineTo(w, toY(4.0)); ctx.stroke(); ctx.setLineDash([]);

    // 4. Energy Wave Area Fill
    const pts = state.energyCurve.filter((p) => p.minute_of_day >= TL_START && p.minute_of_day <= TL_END).map((p) => ({ x: toX(p.minute_of_day), y: toY(p.energy_level), lvl: p.energy_level, min: p.minute_of_day }));
    if (pts.length < 2) return;

    ctx.beginPath(); ctx.moveTo(pts[0].x, h); ctx.lineTo(pts[0].x, pts[0].y);
    for (let i = 0; i < pts.length - 1; i++) ctx.quadraticCurveTo(pts[i].x, pts[i].y, (pts[i].x + pts[i + 1].x) / 2, (pts[i].y + pts[i + 1].y) / 2);
    ctx.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y); ctx.lineTo(pts[pts.length - 1].x, h); ctx.closePath();
    const fillG = ctx.createLinearGradient(0, 0, 0, h);
    fillG.addColorStop(0, "rgba(0, 240, 255, 0.32)"); fillG.addColorStop(0.5, "rgba(176, 38, 255, 0.16)"); fillG.addColorStop(1, "rgba(5, 8, 17, 0.0)");
    ctx.fillStyle = fillG; ctx.fill();

    // 5. Glowing Stroke Line
    ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 0; i < pts.length - 1; i++) ctx.quadraticCurveTo(pts[i].x, pts[i].y, (pts[i].x + pts[i + 1].x) / 2, (pts[i].y + pts[i + 1].y) / 2);
    ctx.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y);
    const strokeG = ctx.createLinearGradient(0, 0, w, 0);
    pts.forEach((pt) => strokeG.addColorStop(Math.max(0, Math.min(1, pt.x / w)), pt.lvl >= 7.5 ? "#00f0ff" : (pt.lvl <= 4.0 ? "#ffd166" : "#b026ff")));
    ctx.shadowColor = "rgba(0, 240, 255, 0.85)"; ctx.shadowBlur = 14;
    ctx.strokeStyle = strokeG; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.shadowBlur = 0;

    // Update Laser needle position
    updateLaserNeedle();
  }

  function updateLaserNeedle() {
    const needle = byId("simulation-laser-needle");
    if (!needle) return;
    const pct = Math.max(0, Math.min(1, (state.simCurrentMinute - TL_START) / TL_SPAN));
    needle.style.left = `${(pct * 100).toFixed(2)}%`;
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
      const left = ((Math.max(TL_START, sM) - TL_START) / TL_SPAN) * 100, width = Math.max(4.0, ((Math.min(TL_END, eM) - Math.max(TL_START, sM)) / TL_SPAN) * 100);
      const meta = getLoadMeta(s.load_type), card = document.createElement("div");
      card.className = `timeline-slot-task ${meta.cls} ${s.is_auto_recovery ? "slot-auto-recovery" : ""}`;
      card.style.left = `${left.toFixed(2)}%`; card.style.width = `${width.toFixed(2)}%`; card.draggable = true;
      card.title = `Húzd új időpontra, vagy kattints a Zen Fókuszhoz: ${s.title}`;
      card.innerHTML = `<div class="slot-time">${esc(s.start_time)} - ${esc(s.end_time)}</div><div class="slot-title">${meta.icon} ${esc(s.title)}</div><div class="slot-meta"><span>${meta.name}</span><span class="slot-energy-badge">⚡ ${s.average_energy_level.toFixed(1)}</span></div>`;

      card.addEventListener("dragstart", (e) => {
        state.draggedTaskId = s.task_id;
        card.classList.add("dragging");
        e.dataTransfer.setData("text/plain", s.task_id);
      });
      card.addEventListener("dragend", () => {
        card.classList.remove("dragging");
        state.draggedTaskId = null;
      });
      card.addEventListener("click", () => openZenFocus(s));
      c.appendChild(card);
    });
  }

  function renderBacklog() {
    const c = byId("task-backlog"), countBadge = byId("backlog-count"); if (!c) return;
    const scheduledIds = new Set(state.scheduledTasks.map((s) => s.task_id)), backlog = state.tasks.filter((t) => !scheduledIds.has(t.id));
    if (countBadge) countBadge.textContent = `${backlog.length} feladat`;
    c.innerHTML = "";
    if (!backlog.length) { c.innerHTML = `<span style="font-size:0.8rem;color:var(--text-muted);padding:12px;">Minden feladat az idővonalra van rendezve! ✨</span>`; return; }
    backlog.forEach((t) => {
      const meta = getLoadMeta(t.load_type), cap = document.createElement("div");
      cap.className = `backlog-capsule ${meta.cls}`; cap.draggable = true;
      const decBtn = t.duration_minutes > 60 ? `<button type="button" class="btn-decompose-task" title="Kognitív bontás 3 fázisra">⚡ Bontás</button>` : "";
      cap.innerHTML = `<span class="capsule-icon">${meta.icon}</span><span class="capsule-title">${esc(t.title)}</span><span class="capsule-dur">${t.duration_minutes}m</span>${decBtn}<button type="button" class="capsule-btn-delete" title="Törlés">✕</button>`;

      cap.addEventListener("dragstart", (e) => {
        state.draggedTaskId = t.id;
        cap.classList.add("dragging");
        e.dataTransfer.setData("text/plain", t.id);
      });
      cap.addEventListener("dragend", () => {
        cap.classList.remove("dragging");
        state.draggedTaskId = null;
      });
      cap.addEventListener("click", (e) => {
        if (!e.target.classList.contains("capsule-btn-delete") && !e.target.classList.contains("btn-decompose-task")) openZenFocus(t);
      });
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
      if (rec) rec.textContent = r.is_overloaded ? "⚠️ Túlterhelés! Húzz be regenerációs sávokat vagy használj Re-flow-t." : "Optimális energiamérleg! A feladatok illeszkednek a ritmusodhoz.";
    }
    const pEl = byId("stats-peak-hours"), cEl = byId("stats-caffeine-window"), dEl = byId("stats-dip-hours");
    if (pEl) pEl.textContent = state.profile.peak_hours.map((p) => `${p.start} - ${p.end}`).join(" & ");
    if (dEl) dEl.textContent = state.profile.dip_hours.map((d) => `${d.start} - ${d.end}`).join(" & ");
    if (cEl && state.caffeineWindow) cEl.textContent = `${state.caffeineWindow.caffeine_start_time} - ${state.caffeineWindow.caffeine_cutoff_time}`;
  }

  function updateTelemetryHub() {
    const alignEl = byId("telemetry-alignment"), cafEl = byId("telemetry-caffeine-time"), melaEl = byId("telemetry-melatonin-gate"), ultraEl = byId("telemetry-ultradian-count"), dopaEl = byId("telemetry-dopamine-guard");
    const deepTasks = state.scheduledTasks.filter((t) => t.load_type === "deep_work");
    const alignPct = deepTasks.length ? Math.min(100, Math.round((deepTasks.filter((t) => t.average_energy_level >= 7.0).length / deepTasks.length) * 100)) : 95;
    if (alignEl) alignEl.textContent = `${alignPct}%`;
    if (cafEl && state.caffeineWindow) cafEl.textContent = state.caffeineWindow.caffeine_cutoff_time;

    const sleepM = timeToMin(state.profile.sleep_time);
    const melaM = (sleepM - 120 + 1440) % 1440;
    if (melaEl) melaEl.textContent = minToTime(melaM);

    const totalDur = state.scheduledTasks.reduce((acc, t) => acc + t.duration_minutes, 0);
    const bracCycles = Math.max(1, Math.floor(totalDur / 90));
    if (ultraEl) ultraEl.textContent = `${bracCycles} BRAC Ciklus`;
    if (dopaEl) dopaEl.textContent = state.debtReport && state.debtReport.is_overloaded ? "82% Csökkent" : "98% Optimális";
  }

  // --- Time Machine Simulation Controller (SPEC-008) ---
  function evaluateSimulationStep() {
    const curT = minToTime(state.simCurrentMinute);
    const clockEl = byId("tm-sim-clock");
    const zoneBadge = byId("tm-sim-zone");
    if (clockEl) clockEl.textContent = curT;

    let isPeak = state.profile.peak_hours.some((p) => timeToMin(p.start) <= state.simCurrentMinute && state.simCurrentMinute <= timeToMin(p.end));
    let isDip = state.profile.dip_hours.some((d) => timeToMin(d.start) <= state.simCurrentMinute && state.simCurrentMinute <= timeToMin(d.end));

    let currentZone = "MODERATE";
    if (isPeak) currentZone = "PEAK";
    else if (isDip) currentZone = "DIP";
    else if (state.simCurrentMinute >= timeToMin(state.profile.sleep_time) - 120) currentZone = "RECOVERY";

    if (zoneBadge) {
      zoneBadge.className = `tm-zone-badge zone-${currentZone.toLowerCase()}`;
      if (currentZone === "PEAK") zoneBadge.textContent = "🚀 FÓKUSZCSÚCS (⚡ 8.8/10)";
      else if (currentZone === "DIP") zoneBadge.textContent = "🍲 KAJA-KÓMA (⚡ 3.5/10)";
      else if (currentZone === "RECOVERY") zoneBadge.textContent = "🌙 ESTI REGENERÁCIÓ (⚡ 2.0/10)";
      else zoneBadge.textContent = "💡 KIEGYENSÚLYOZOTT (⚡ 6.8/10)";
    }

    // Trigger Neuro-Chime on Zone Change
    if (currentZone !== state.lastChimedZone) {
      if (currentZone === "PEAK") playNeuroChime(528, 0.9);
      else if (currentZone === "DIP") playNeuroChime(396, 0.7);
      else if (currentZone === "RECOVERY") playNeuroChime(432, 1.2);
      state.lastChimedZone = currentZone;
    }

    updateLaserNeedle();
  }

  function toggleTimeMachine() {
    state.simIsPlaying = !state.simIsPlaying;
    const playBtn = byId("btn-tm-play");
    if (state.simIsPlaying) {
      if (playBtn) { playBtn.textContent = "⏸️ Szünet"; playBtn.classList.add("active"); }
      state.simTimer = setInterval(() => {
        state.simCurrentMinute += 5;
        if (state.simCurrentMinute > TL_END) state.simCurrentMinute = TL_START;
        evaluateSimulationStep();
      }, 1000 / state.simSpeed);
    } else {
      if (playBtn) { playBtn.textContent = "▶ Szimuláció Indítása"; playBtn.classList.remove("active"); }
      if (state.simTimer) clearInterval(state.simTimer);
    }
  }

  function setupTimeMachineHUD() {
    byId("btn-tm-play")?.addEventListener("click", toggleTimeMachine);
    byId("btn-tm-reset")?.addEventListener("click", () => {
      state.simCurrentMinute = TL_START;
      evaluateSimulationStep();
      showToast("⏰ Szimuláció visszaállítva 06:00-ra!");
    });
    byId("btn-tm-speed")?.addEventListener("click", () => {
      state.simSpeed = state.simSpeed === 1 ? 5 : (state.simSpeed === 5 ? 15 : 1);
      byId("btn-tm-speed").textContent = `⏩ ${state.simSpeed}x Sebesség`;
      if (state.simIsPlaying) {
        clearInterval(state.simTimer);
        state.simTimer = setInterval(() => {
          state.simCurrentMinute += 5;
          if (state.simCurrentMinute > TL_END) state.simCurrentMinute = TL_START;
          evaluateSimulationStep();
        }, 1000 / state.simSpeed);
      }
    });
    byId("btn-tm-chime")?.addEventListener("click", () => {
      state.chimeEnabled = !state.chimeEnabled;
      const b = byId("btn-tm-chime");
      b.classList.toggle("active", state.chimeEnabled);
      b.textContent = state.chimeEnabled ? "🔔 Neuro-Chime: BE" : "🔕 Neuro-Chime: KI";
      showToast(state.chimeEnabled ? "🔔 Bio-akusztikus jelzések bekapcsolva" : "🔕 Jelzések elnémítva");
    });
    evaluateSimulationStep();
  }

  // --- Setup Canvas, D&D and Event Listeners ---
  function setupInteractiveCanvas() {
    const cvs = byId("energy-wave-canvas"), tip = byId("curve-tooltip");
    if (!cvs || !tip) return;
    cvs.addEventListener("mousemove", (e) => {
      const r = cvs.getBoundingClientRect(), mouseX = e.clientX - r.left, pct = Math.max(0, Math.min(1, mouseX / r.width)), curM = TL_START + pct * TL_SPAN, curT = minToTime(curM);
      const pt = state.energyCurve.find((p) => Math.abs(p.minute_of_day - curM) <= 15), lvl = pt ? pt.energy_level.toFixed(1) : "7.0";
      let zone = "Kiegyensúlyozott";
      if (state.profile.peak_hours.some((p) => timeToMin(p.start) <= curM && curM <= timeToMin(p.end))) zone = "🚀 Fókuszcsúcs";
      else if (state.profile.dip_hours.some((d) => timeToMin(d.start) <= curM && curM <= timeToMin(d.end))) zone = "🍲 Mélypont";
      tip.classList.remove("hidden");
      tip.style.left = `${Math.min(r.width - 120, Math.max(10, mouseX - 50))}px`;
      tip.style.top = "10px";
      tip.innerHTML = `<strong>${curT}</strong> | ⚡ ${lvl}/10<br><span style="color:var(--cyan-neon)">${zone}</span>`;
    });
    cvs.addEventListener("mouseleave", () => tip.classList.add("hidden"));

    cvs.addEventListener("click", (e) => {
      const r = cvs.getBoundingClientRect(), pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), clickedM = Math.round((TL_START + pct * TL_SPAN) / 15) * 15;
      state.simCurrentMinute = clickedM;
      evaluateSimulationStep();
      if (clickedM < 780) {
        state.profile.peak_hours[0] = { start: minToTime(clickedM), end: minToTime(clickedM + 150) };
        showToast(`🎯 Délelőtti fókuszcsúcs áthelyezve: ${state.profile.peak_hours[0].start} - ${state.profile.peak_hours[0].end}`);
      } else {
        state.profile.peak_hours[1] = { start: minToTime(clickedM), end: minToTime(clickedM + 120) };
        showToast(`🎯 Délutáni fókuszcsúcs áthelyezve: ${state.profile.peak_hours[1].start} - ${state.profile.peak_hours[1].end}`);
      }
      renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule();
    });

    byId("btn-tune-peak1")?.addEventListener("click", () => { const p = state.profile.peak_hours[0]; if (p) { p.end = minToTime(timeToMin(p.end) + 30); showToast(`🚀 Délelőtti csúcs kinyújtva: ${p.start} - ${p.end}`); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); } });
    byId("btn-tune-peak2")?.addEventListener("click", () => { const p = state.profile.peak_hours[1]; if (p) { p.end = minToTime(timeToMin(p.end) + 30); showToast(`🚀 Délutáni csúcs kinyújtva: ${p.start} - ${p.end}`); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); } });
    byId("btn-tune-dip")?.addEventListener("click", () => { const d = state.profile.dip_hours[0]; if (d) { d.start = minToTime(timeToMin(d.start) + 30); d.end = minToTime(timeToMin(d.end) + 30); showToast(`🍲 Mélypont eltolva: ${d.start} - ${d.end}`); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); } });
    byId("btn-tune-reset")?.addEventListener("click", () => { state.profile = JSON.parse(JSON.stringify(PRESETS.standard)); showToast("🎯 Profil visszaállítva!"); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); });
  }

  function setupDragAndDrop() {
    const tl = byId("tasks-timeline"), dock = byId("task-backlog");
    if (tl) {
      tl.addEventListener("dragover", (e) => { e.preventDefault(); tl.classList.add("drag-over"); });
      tl.addEventListener("dragleave", () => tl.classList.remove("drag-over"));
      tl.addEventListener("drop", (e) => {
        e.preventDefault(); tl.classList.remove("drag-over");
        const taskId = e.dataTransfer.getData("text/plain") || state.draggedTaskId; if (!taskId) return;
        const r = tl.getBoundingClientRect(), pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), targetM = Math.round((TL_START + pct * TL_SPAN) / 15) * 15, targetT = minToTime(targetM);
        const task = state.tasks.find((t) => t.id === taskId);
        if (task) { task.is_fixed = true; task.start_time = targetT; showToast(`📍 '${task.title}' fixálva ${targetT}-kor!`); }
        runAutoSchedule();
      });
    }
    if (dock) {
      dock.addEventListener("dragover", (e) => { e.preventDefault(); dock.classList.add("drag-over-dock"); });
      dock.addEventListener("dragleave", () => dock.classList.remove("drag-over-dock"));
      dock.addEventListener("drop", (e) => {
        e.preventDefault(); dock.classList.remove("drag-over-dock");
        const taskId = e.dataTransfer.getData("text/plain") || state.draggedTaskId; if (!taskId) return;
        const task = state.tasks.find((t) => t.id === taskId);
        if (task) { task.is_fixed = false; delete task.start_time; showToast(`🎒 '${task.title}' visszatéve a Backlog dokkba!`); }
        runAutoSchedule();
      });
    }
  }

  async function decomposeTask(t) {
    try {
      const res = await fetch("/api/v1/energy/decompose-task", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ task: t }) });
      if (res.ok) {
        const d = await res.json(); state.tasks = state.tasks.filter((x) => x.id !== t.id);
        (d.subtasks || []).forEach((st, idx) => { state.tasks.push({ id: `sub-${t.id}-${idx}-${Date.now()}`, title: st.title, duration_minutes: st.duration_minutes, load_type: st.load_type, energy_cost: st.energy_cost, is_fixed: false }); });
        showToast(`⚡ Feladat felbontva 3 fázisra!`); renderBacklog(); runAutoSchedule();
      }
    } catch (e) { showToast("⚠️ Hiba a feladatbontáskor!", true); }
  }

  function openZenFocus(task) {
    state.zenActiveTask = task;
    const modal = byId("zen-focus-modal"); if (!modal) return;
    byId("zen-task-title").textContent = task.title;
    byId("zen-task-load").textContent = getLoadMeta(task.load_type).name.toUpperCase();
    byId("zen-task-energy").textContent = `⚡ ${(task.energy_cost || task.average_energy_level || 8.0).toFixed(1)}`;
    state.zenSeconds = (task.duration_minutes || 25) * 60;
    const disp = byId("zen-timer-display");
    const updateTimer = () => { const m = Math.floor(state.zenSeconds / 60), s = state.zenSeconds % 60; disp.textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`; };
    updateTimer();
    if (state.zenTimer) clearInterval(state.zenTimer);
    state.zenTimer = setInterval(() => { if (state.zenSeconds > 0) { state.zenSeconds--; updateTimer(); } else { clearInterval(state.zenTimer); showToast("🔔 Zen Fókusz blokk véget ért!"); } }, 1000);
    modal.classList.remove("hidden");
  }

  function closeZenFocus() { const modal = byId("zen-focus-modal"); if (modal) modal.classList.add("hidden"); if (state.zenTimer) clearInterval(state.zenTimer); stopZenAudio(); state.zenActiveTask = null; }
  async function completeZenTask() { if (state.zenActiveTask) { const id = state.zenActiveTask.task_id || state.zenActiveTask.id; state.tasks = state.tasks.filter((t) => t.id !== id); } closeZenFocus(); await runReflowDay(); showToast("✓ Feladat kész! A nap újrahangolva."); }

  function setupEventListeners() {
    const input = byId("quick-task-input"), addBtn = byId("btn-add-task"), autoBtn = byId("btn-auto-schedule"), reflowBtn = byId("btn-reflow-now"), cafBtn = byId("btn-toggle-caffeine"), sSlider = byId("sleep-quality-slider"), sLabel = byId("sleep-quality-label"), expBtn = byId("btn-export-ics");

    async function handleAdd() {
      const text = input ? input.value.trim() : ""; if (!text) return;
      const p = await parseTaskNLP(text);
      state.tasks.push({ id: `task-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, title: p.title, duration_minutes: p.duration_minutes, load_type: p.load_type, energy_cost: p.energy_cost, is_fixed: false });
      if (input) input.value = ""; renderBacklog(); runAutoSchedule();
    }
    if (addBtn) addBtn.addEventListener("click", handleAdd);
    if (input) input.addEventListener("keydown", (e) => { if (e.key === "Enter") handleAdd(); });
    if (autoBtn) autoBtn.addEventListener("click", runAutoSchedule);
    if (reflowBtn) reflowBtn.addEventListener("click", runReflowDay);
    if (expBtn) expBtn.addEventListener("click", () => {
      fetch("/api/v1/energy/calendar/export-ics", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scheduled_tasks: state.scheduledTasks, calendar_name: "Cirkadián Naptár" }) })
        .then(r => r.blob()).then(b => { const u = URL.createObjectURL(b), a = document.createElement("a"); a.href = u; a.download = "energy-calendar.ics"; a.click(); a.remove(); showToast("📤 Naptár (.ics) letöltve!"); });
    });
    if (cafBtn) cafBtn.addEventListener("click", () => { state.showCaffeineWindow = !state.showCaffeineWindow; cafBtn.classList.toggle("active", state.showCaffeineWindow); renderCanvasCurve(); showToast(state.showCaffeineWindow ? "☕ Koffein Sáv bekapcsolva" : "Koffein Sáv elrejtve"); });
    if (sSlider) sSlider.addEventListener("input", (e) => { const val = parseInt(e.target.value, 10); state.sleepQuality = val / 100.0; if (sLabel) sLabel.textContent = `🌙 Vitalitás: ${val}%`; runReflowDay(); });

    byId("btn-close-zen")?.addEventListener("click", closeZenFocus);
    byId("btn-zen-complete")?.addEventListener("click", completeZenTask);
    byId("btn-toggle-zen-audio")?.addEventListener("click", toggleZenAudio);

    document.querySelectorAll(".example-chip").forEach((chip) => chip.addEventListener("click", () => { if (input) { input.value = chip.dataset.example || ""; handleAdd(); } }));
    document.querySelectorAll(".preset-btn").forEach((btn) => btn.addEventListener("click", () => { const key = btn.dataset.preset; if (!PRESETS[key]) return; document.querySelectorAll(".preset-btn").forEach((b) => b.classList.remove("active")); btn.classList.add("active"); state.profile = JSON.parse(JSON.stringify(PRESETS[key])); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); }));

    byId("btn-toggle-profile")?.addEventListener("click", () => byId("profile-modal")?.classList.remove("hidden"));
    byId("btn-close-modal")?.addEventListener("click", () => byId("profile-modal")?.classList.add("hidden"));
    byId("btn-cancel-modal")?.addEventListener("click", () => byId("profile-modal")?.classList.add("hidden"));

    byId("profile-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      state.profile.wake_time = byId("input-wake-time").value; state.profile.sleep_time = byId("input-sleep-time").value;
      state.profile.peak_hours = [{ start: byId("input-peak1-start").value, end: byId("input-peak1-end").value }, { start: byId("input-peak2-start").value, end: byId("input-peak2-end").value }];
      state.profile.dip_hours = [{ start: byId("input-dip-start").value, end: byId("input-dip-end").value }];
      byId("profile-modal")?.classList.add("hidden"); renderTimelineMarkers(); fetchEnergyCurve(); runAutoSchedule(); showToast("✓ Profil elmentve!");
    });
    window.addEventListener("resize", renderCanvasCurve);
  }

  document.addEventListener("DOMContentLoaded", async () => {
    renderTimelineMarkers();
    setupDragAndDrop();
    setupInteractiveCanvas();
    setupTimeMachineHUD();
    setupEventListeners();
    await fetchCaffeineWindow();
    await fetchEnergyCurve();
    await runAutoSchedule();
  });
})();
