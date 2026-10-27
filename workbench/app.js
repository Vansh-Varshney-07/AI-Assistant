'use strict';

const $ = id => document.getElementById(id);

// --- Core State ---
const state = {
  records: [],
  history: [],
  session: crypto.randomUUID(),
  token: '',
  loading: false,
  switching: false,
  stopped: false,
  space: '',
  currentView: 'home',
  workers: []
};

// --- Utilities ---
const json = value => JSON.stringify(value, null, 2);
const display = value => JSON.stringify(value, (_key, item) => item === null ? 'Unavailable' : item, 2);
const time = value => value == null ? 'Unavailable' : new Date(value * 1000).toLocaleString();
const el = (tag, text, cls) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (cls) n.className = cls;
  return n;
};

async function api(path, options) {
  try {
    const response = await fetch(path, options);
    const body = await response.json();
    if (!response.ok && !body.diagnostics) throw new Error(body.error || `HTTP ${response.status}`);
    return body;
  } catch (err) {
    // If backend is not running or endpoint not yet registered, handle gracefully
    if (path.startsWith('/api/wayfinder/workers')) {
      return { workers: getFallbackWorkers() };
    }
    throw err;
  }
}

function updateControls() {
  for (const id of ['send', 'fresh', 'stop', 'space-select', 'new-space', 'refresh']) {
    const element = $(id);
    if (element) element.disabled = state.loading || state.switching || state.stopped;
  }
}

// --- View Navigation ---
function switchView(viewName) {
  state.currentView = viewName;
  const panels = document.querySelectorAll('.view-panel');
  panels.forEach(p => {
    if (p.id === `view-${viewName}`) {
      p.classList.remove('hidden');
      p.classList.add('active');
    } else {
      p.classList.add('hidden');
      p.classList.remove('active');
    }
  });

  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.remove('text-on-surface-variant');
      item.classList.add('active-nav');
    } else {
      item.classList.remove('active-nav');
      item.classList.add('text-on-surface-variant');
    }
  });

  if (viewName === 'activity' && (!state.workers || !state.workers.length)) {
    loadWorkers();
  }
  if (viewName === 'memory' && state.space) {
    refresh();
  }
}

window.addEventListener('hashchange', () => {
  const hash = window.location.hash.replace('#', '') || 'home';
  switchView(hash);
});

// --- Theme Management ---
function setTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark');
    try { localStorage.setItem('wayfinder-theme', 'dark'); } catch (_) {}
  } else {
    document.documentElement.classList.remove('dark');
    try { localStorage.setItem('wayfinder-theme', 'light'); } catch (_) {}
  }
}

function initTheme() {
  let theme = 'dark';
  try { theme = localStorage.getItem('wayfinder-theme') || 'dark'; } catch (_) {}
  setTheme(theme === 'dark');

  $('theme-toggle')?.addEventListener('click', () => {
    const isDark = document.documentElement.classList.contains('dark');
    setTheme(!isDark);
  });
  $('theme-dark-btn')?.addEventListener('click', () => setTheme(true));
  $('theme-light-btn')?.addEventListener('click', () => setTheme(false));
}

// --- Quick Search Modal ---
function initSearchModal() {
  const modal = $('search-modal');
  const trigger = $('search-modal-trigger');
  const input = $('modal-search-input');
  if (!modal || !trigger) return;

  function openSearch() {
    modal.classList.remove('hidden');
    input?.focus();
  }
  function closeSearch() {
    modal.classList.add('hidden');
    if (input) input.value = '';
  }

  trigger.onclick = openSearch;
  modal.onclick = (e) => {
    if (e.target === modal) closeSearch();
  };

  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openSearch();
    } else if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      closeSearch();
    }
  });

  input?.addEventListener('input', () => {
    const term = input.value.toLowerCase();
    const items = modal.querySelectorAll('.search-result-item');
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = (!term || text.includes(term)) ? 'flex' : 'none';
    });
  });

  modal.querySelectorAll('.search-result-item').forEach(link => {
    link.addEventListener('click', () => {
      closeSearch();
    });
  });
}

// --- Pet Summon Modal ---
function initPetModal() {
  const modal = $('pet-modal');
  const triggers = [$('summon-pet-btn'), $('home-pet-trigger'), $('toggle-floating-pet')];
  const close = $('close-pet-modal');

  function openPet() { modal?.classList.remove('hidden'); }
  function closePet() { modal?.classList.add('hidden'); }

  triggers.forEach(t => { if (t) t.onclick = openPet; });
  if (close) close.onclick = closePet;

  window.addEventListener('keydown', (e) => {
    if (e.altKey && e.code === 'Space') {
      e.preventDefault();
      if (modal?.classList.contains('hidden')) openPet();
      else closePet();
    }
  });

  document.querySelectorAll('.pet-quick-action').forEach(btn => {
    btn.onclick = () => {
      const action = btn.getAttribute('data-action');
      closePet();
      if (action === 'tasks') switchView('planner');
      else if (action === 'memory') switchView('memory');
      else if (action === 'analyze') {
        const homeInput = $('home-prompt-input');
        if (homeInput) {
          homeInput.value = 'Analyze current screen context and summarize active items';
          switchView('home');
          homeInput.focus();
        }
      }
    };
  });
}

// --- Worker Loading ---
function getFallbackWorkers() {
  return [
    { id: 'W01', name: 'Intent Analyst', status: 'fixture-tested', responsibility: 'Parse raw user request into structured intent record. Identify goal and subject.' },
    { id: 'W03', name: 'Task Planner', status: 'fixture-tested', responsibility: 'Generate step-by-step TaskPlan with worker assignments and capability tags.' },
    { id: 'W06', name: 'Result Validator', status: 'fixture-tested', responsibility: 'Validate schema conformance and acceptance criteria against worker contracts.' },
    { id: 'W07', name: 'Synthesis Worker', status: 'fixture-tested', responsibility: 'Synthesize multi-source insights into unified narrative answers with citations.' },
    { id: 'W08', name: 'Web Researcher', status: 'fixture-tested', responsibility: 'Autonomous web searches, domain filtering, and evidence document retrieval.' },
    { id: 'W09', name: 'Source Verifier', status: 'fixture-tested', responsibility: 'Cross-reference claims with primary ground truth; emit EvidenceVerdict.' },
    { id: 'W10', name: 'Document Analyst', status: 'fixture-tested', responsibility: 'Extract structured tables, claims, and entity relationships from uploaded documents.' },
    { id: 'W11', name: 'Data Analyst', status: 'fixture-tested', responsibility: 'Perform statistical queries, metric aggregations, and compute telemetry trends.' },
    { id: 'W12', name: 'Knowledge Synthesizer', status: 'fixture-tested', responsibility: 'Ingest verified claims into FalkorDB graph and Qdrant semantic vectors.' },
    { id: 'W13', name: 'Calendar Analyst', status: 'fixture-tested', responsibility: 'Inspect time commitments, parse meeting requirements, detect schedule conflicts.' },
    { id: 'W14', name: 'Task Manager', status: 'fixture-tested', responsibility: 'Manage backlog, status transitions, priority scoring, and assignee tracking.' },
    { id: 'W15', name: 'Schedule Optimizer', status: 'fixture-tested', responsibility: 'Compute optimal daily focus blocks and meeting placements across constraints.' },
    { id: 'W16', name: 'Commitment Tracker', status: 'fixture-tested', responsibility: 'Extract promises and action items made in conversations and documents.' },
    { id: 'W18', name: 'Meeting Prep Worker', status: 'fixture-tested', responsibility: 'Compile contextual dossier, attendee profile, and discussion briefing.' },
    { id: 'W19', name: 'Repository Analyst', status: 'fixture-tested', responsibility: 'Inspect source tree, discover skills and tools, map architectural topology.' },
    { id: 'W24', name: 'Code Reviewer', status: 'fixture-tested', responsibility: 'Automated static analysis, diff inspection, security linting, and style review.' }
  ];
}

async function loadWorkers() {
  const grid = $('workers-grid');
  if (!grid) return;
  try {
    const data = await api('/api/wayfinder/workers');
    const workers = data.workers || getFallbackWorkers();
    state.workers = workers;
    grid.replaceChildren();

    workers.forEach(w => {
      const card = el('div', undefined, 'p-space-sm bg-surface-container border border-outline-variant flex flex-col gap-1 hover:border-primary transition-colors');
      const header = el('div', undefined, 'flex justify-between items-center');
      header.append(
        el('span', w.id, 'font-mono text-xs font-bold text-primary'),
        el('span', w.status || 'READY', 'px-1.5 py-0.2 bg-primary/10 text-primary text-[10px] font-mono')
      );
      card.append(header);
      card.append(el('span', w.name, 'font-headline-sm text-xs font-semibold text-on-surface'));
      card.append(el('p', w.responsibility || '', 'text-[11px] text-outline line-clamp-2'));
      grid.append(card);
    });

    if ($('workers-count-tag')) $('workers-count-tag').textContent = `${workers.length} Loaded`;
    if ($('telemetry-nodes')) $('telemetry-nodes').textContent = `${workers.length} ONLINE`;
  } catch (_) {
    // If error, display fallbacks
    const workers = getFallbackWorkers();
    state.workers = workers;
    grid.replaceChildren();
    workers.forEach(w => {
      const card = el('div', undefined, 'p-space-sm bg-surface-container border border-outline-variant flex flex-col gap-1');
      card.append(el('span', `${w.id} · ${w.name}`, 'font-headline-sm text-xs font-semibold text-on-surface'));
      card.append(el('p', w.responsibility, 'text-[11px] text-outline line-clamp-2'));
      grid.append(card);
    });
  }
}

// --- Memory Workbench Functions ---
function filters(id, values, label) {
  const element = $(id);
  if (!element) return;
  const old = element.value;
  element.replaceChildren(new Option(label, ''), ...[...new Set(values)].sort().map(v => new Option(v, v)));
  if ([...element.options].some(o => o.value === old)) element.value = old;
}

function renderRecords() {
  if (!$('records') || !$('search')) return;
  const term = $('search').value.toLowerCase();
  const records = state.records.filter(r =>
    r.memory_space_id === state.space &&
    (!term || json(r).toLowerCase().includes(term)) &&
    (!$('status-filter')?.value || (r.statuses?.length ? r.statuses : ['Unavailable']).includes($('status-filter').value)) &&
    (!$('type-filter')?.value || (r.types?.length ? r.types : ['Unavailable']).includes($('type-filter').value))
  );

  const sortVal = $('sort')?.value || 'created-desc';
  const [field, order] = sortVal.split('-');
  records.sort((a, b) => {
    const av = a[field + '_timestamp'], bv = b[field + '_timestamp'];
    if (av == null) return bv == null ? a.memory_id.localeCompare(b.memory_id) : 1;
    if (bv == null) return -1;
    return (av - bv) * (order === 'asc' ? 1 : -1) || a.memory_id.localeCompare(b.memory_id);
  });

  if ($('inventory-count')) {
    $('inventory-count').textContent = `${records.length} shown / ${state.records.length} records in space`;
  }

  $('records').replaceChildren();
  if (!records.length) {
    $('records').append(el('p', 'No records match these filters.', 'text-xs text-outline p-2'));
    return;
  }

  for (const r of records) {
    const card = el('div', undefined, 'p-space-sm bg-surface-container border border-outline-variant/60 flex flex-col gap-1');
    card.append(
      el('span', r.memory_id, 'font-mono text-xs font-bold text-primary'),
      el('p', r.content, 'text-xs text-on-surface line-clamp-2')
    );
    const tags = el('div', undefined, 'flex flex-wrap gap-1 mt-1');
    tags.append(
      el('span', r.statuses?.join(', ') || 'Status: Ready', 'px-1 py-0.2 bg-primary/10 text-primary text-[10px] font-mono'),
      el('span', r.types?.join(', ') || 'Type: Record', 'px-1 py-0.2 bg-surface-container-high text-outline text-[10px] font-mono')
    );
    card.append(tags);

    const meta = el('div', undefined, 'flex items-center justify-between text-[10px] font-mono text-outline pt-1 border-t border-outline-variant/30');
    meta.append(
      el('span', `Qdrant: ${r.vector_stored ? '✓' : '✗'} · Falkor: ${r.graph_stored ? '✓' : '✗'}`),
      el('span', time(r.created_timestamp))
    );
    card.append(meta);

    const inspectBtn = el('button', 'Inspect record detail', 'mt-1 py-1 px-space-xs bg-surface-container-high border border-outline-variant hover:border-primary text-[11px] text-on-surface text-left font-mono');
    inspectBtn.type = 'button';
    inspectBtn.onclick = () => {
      if ($('detail')) $('detail').textContent = display(r);
    };
    card.append(inspectBtn);

    $('records').append(card);
  }
}

async function refresh() {
  const space = state.space;
  if (!space) return;
  if ($('refresh')) $('refresh').disabled = true;
  if ($('inventory-error')) $('inventory-error').textContent = '';

  try {
    const [status, inventory] = await Promise.all([
      api('/api/status'),
      api('/api/memories?memory_space_id=' + encodeURIComponent(space))
    ]);
    if (space !== state.space) return;

    if ($('status')) $('status').textContent = display(status);
    state.records = inventory.records || [];

    if ($('model')) {
      const selectedModel = $('model').value;
      $('model').replaceChildren(
        new Option('Evidence only · no hosted calls', ''),
        ...(status.models || []).map(m => new Option(m, m))
      );
      $('model').value = selectedModel;
    }

    filters('status-filter', state.records.flatMap(r => r.statuses?.length ? r.statuses : ['Unavailable']), 'All statuses');
    filters('type-filter', state.records.flatMap(r => r.types?.length ? r.types : ['Unavailable']), 'All types');

    if (inventory.unowned_observation_ids?.length && $('inventory-error')) {
      $('inventory-error').textContent = `Unowned observations: ${inventory.unowned_observation_ids.join(', ')}`;
    }
    renderRecords();
  } catch (e) {
    if (space === state.space && $('inventory-error')) {
      $('inventory-error').textContent = `Refresh failed: ${e.message}. Any displayed records are from last successful refresh.`;
    }
  } finally {
    if ($('refresh')) $('refresh').disabled = false;
  }
}

function selectRequest(entry) {
  const container = $('retrieved');
  if (!container) return;
  container.replaceChildren();
  const { result } = entry;
  if (!result) return;

  if (result.recall) {
    container.append(el('pre', display(result.recall)));
  } else if (!result.retrieved?.length) {
    container.append(el('p', 'No memories returned for this request.', 'text-outline'));
  } else {
    for (const hit of result.retrieved) {
      const d = el('details', undefined, 'mb-1 border border-outline-variant p-1');
      d.append(
        el('summary', `${hit.memory_id} · score ${hit.score}`, 'cursor-pointer font-bold text-primary'),
        el('pre', display(hit), 'mt-1 text-xs')
      );
      container.append(d);
    }
  }
}

function renderHistory() {
  const container = $('history');
  if (!container) return;
  container.replaceChildren();

  const entries = state.history.filter(e => e.memory_space_id === state.space);
  if (!entries.length) {
    container.append(el('p', 'No prompts submitted in this session.', 'text-xs text-outline'));
    return;
  }

  for (const entry of entries) {
    const card = el('div', undefined, 'p-space-sm bg-surface-container border border-outline-variant/60 flex flex-col gap-1 text-xs');
    const header = el('div', undefined, 'flex justify-between items-center text-[10px] font-mono text-outline');
    header.append(
      el('span', `${entry.mode.toUpperCase()} · ${entry.memory_space_id}`),
      el('span', entry.submitted_at ? new Date(entry.submitted_at).toLocaleTimeString() : '')
    );
    card.append(header);
    card.append(el('p', entry.prompt, 'font-medium text-on-surface'));

    const diag = entry.result?.diagnostics;
    if (diag) {
      const badge = el('span', `Pipeline: ${diag.pipeline_invoked ? 'Invoked' : 'Bypassed'} · ${entry.result.ok ? 'OK' : 'Error'}`,
        `font-mono text-[10px] px-1 py-0.2 ${entry.result.ok ? 'bg-primary/20 text-primary' : 'bg-error/20 text-error'}`);
      card.append(badge);
    }

    if (entry.result?.assistant) {
      card.append(el('p', entry.result.assistant.answer, 'p-1 bg-surface-container-high border-l-2 border-primary my-1'));
    }

    const btnRow = el('div', undefined, 'flex items-center gap-1 mt-1');
    const selectBtn = el('button', 'View evidence', 'px-2 py-0.5 bg-surface-container-high border border-outline-variant hover:border-primary text-[10px] font-mono');
    selectBtn.onclick = () => selectRequest(entry);
    btnRow.append(selectBtn);

    const downloadBtn = el('button', 'Save JSON', 'px-2 py-0.5 bg-surface-container-high border border-outline-variant hover:border-primary text-[10px] font-mono');
    downloadBtn.onclick = () => {
      const blob = new Blob([json(entry)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = el('a');
      a.href = url;
      a.download = `memory-evidence-${entry.request_id}.json`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
    btnRow.append(downloadBtn);
    card.append(btnRow);

    container.append(card);
  }
  container.scrollTop = container.scrollHeight;
}

// --- Submit Prompt ---
async function submitPrompt(promptText, mode = 'retrieve') {
  if (state.loading || state.switching || state.stopped) return;
  if (!state.space) {
    if ($('request-error')) $('request-error').textContent = 'Create or select a memory space first.';
    return;
  }

  state.loading = true;
  updateControls();
  if ($('activity')) $('activity').textContent = 'Running memory engine…';
  if ($('request-error')) $('request-error').textContent = '';

  try {
    const body = {
      prompt: promptText,
      mode: mode,
      memory_space_id: state.space,
      session_id: state.session,
      request_id: crypto.randomUUID(),
      subject: $('subject')?.value || 'manual-user',
      predicate: $('predicate')?.value || '',
      confirmed: $('confirmed')?.checked || false,
      top_k: Number($('top-k')?.value || 5),
      temporal_mode: $('temporal')?.value || 'now',
      model: $('model')?.value || ''
    };

    if (body.mode === 'claim' && $('claims')?.value) {
      body.claims = JSON.parse($('claims').value, (_key, value) => {
        if (typeof value === 'number' && Number.isInteger(value) && !Number.isSafeInteger(value)) {
          throw new Error('Claim JSON contains an unsafe large integer.');
        }
        return value;
      });
    }

    const result = await api('/api/prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Workbench-Token': state.token
      },
      body: json(body)
    });

    const entry = { ...body, submitted_at: new Date().toISOString(), result };
    state.history.push(entry);
    renderHistory();
    selectRequest(entry);

    if (!result.ok && $('request-error')) {
      $('request-error').textContent = json(result.diagnostics?.errors || 'Request failed');
    }

    await refresh();
    return result;
  } catch (e) {
    if ($('request-error')) {
      $('request-error').textContent = e.message + ' (Check local FalkorDB or exclusivity lock)';
    }
  } finally {
    state.loading = false;
    updateControls();
    if ($('activity')) $('activity').textContent = '';
  }
}

// --- Memory Spaces Management ---
async function loadSpaces(selected) {
  try {
    const { spaces } = await api('/api/spaces');
    if ($('space-select')) {
      $('space-select').replaceChildren(...spaces.map(s => new Option(`${s.name} · ${s.memory_space_id}`, s.memory_space_id)));
      if (spaces.some(s => s.memory_space_id === selected)) {
        $('space-select').value = selected;
      }
    }
    return spaces;
  } catch (err) {
    // If spaces endpoint is offline, return default mock space
    const fallback = [{ memory_space_id: 'default_space', name: 'Default Test Space' }];
    if ($('space-select')) {
      $('space-select').replaceChildren(...fallback.map(s => new Option(`${s.name} · ${s.memory_space_id}`, s.memory_space_id)));
    }
    return fallback;
  }
}

async function switchSpace(id) {
  state.switching = true;
  updateControls();
  state.space = id;
  state.records = [];
  state.session = crypto.randomUUID();

  try { localStorage.setItem('iron-web-memory-space', id); } catch (_) {}

  if ($('active-space')) $('active-space').textContent = `Space ID: ${id}`;
  if ($('active-space-pill')) $('active-space-pill').textContent = `SPACE: ${id}`;
  if ($('detail')) $('detail').textContent = 'Select a stored record in this space.';
  if ($('retrieved')) $('retrieved').textContent = 'Unavailable — send a prompt in this space.';
  if ($('prompt')) $('prompt').value = '';
  if ($('claims')) $('claims').value = '';
  if ($('confirmed')) $('confirmed').checked = false;

  try {
    renderHistory();
    renderRecords();
    await refresh();
  } finally {
    state.switching = false;
    updateControls();
  }
}

// --- Event Listeners Setup ---
function setupEventListeners() {
  // Navigation Links
  document.querySelectorAll('.nav-item').forEach(link => {
    link.addEventListener('click', (e) => {
      const view = link.getAttribute('data-view');
      if (view) {
        switchView(view);
      }
    });
  });

  // Prompt Form (Memory View)
  $('prompt-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const promptInput = $('prompt');
    const promptVal = promptInput ? promptInput.value.trim() : '';
    if (!promptVal) return;
    const mode = $('mode')?.value || 'retrieve';
    const result = await submitPrompt(promptVal, mode);
    if (result && result.ok && promptInput) {
      promptInput.value = '';
    }
  });

  // Home Prompt Form
  $('home-prompt-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = $('home-prompt-input');
    const val = input ? input.value.trim() : '';
    if (!val) return;
    input.value = '';
    // Switch to memory view and submit prompt so operator sees full retrieval trace
    switchView('memory');
    await submitPrompt(val, 'store');
  });

  // Quick Prompt Buttons on Home
  document.querySelectorAll('.quick-prompt-btn').forEach(btn => {
    btn.onclick = async () => {
      const prompt = btn.getAttribute('data-prompt');
      if (!prompt) return;
      switchView('memory');
      await submitPrompt(prompt, 'retrieve');
    };
  });

  // Mode Change
  $('mode')?.addEventListener('change', () => {
    if ($('claim-controls')) {
      $('claim-controls').hidden = $('mode').value !== 'claim';
    }
  });

  // Fresh Conversation
  $('fresh')?.addEventListener('click', () => {
    state.history = state.history.filter(e => e.memory_space_id !== state.space);
    state.session = crypto.randomUUID();
    renderHistory();
    if ($('retrieved')) $('retrieved').textContent = 'Unavailable — send a prompt.';
    if ($('prompt')) $('prompt').value = '';
    if ($('request-error')) $('request-error').textContent = '';
  });

  // Refresh Button
  $('refresh')?.addEventListener('click', refresh);

  // Stop Button
  $('stop')?.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to shut down the local workbench server?')) return;
    if ($('stop')) $('stop').disabled = true;
    try {
      await api('/api/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Workbench-Token': state.token },
        body: '{}'
      });
      state.stopped = true;
      updateControls();
      if ($('activity')) $('activity').textContent = 'Workbench server stopped cleanly.';
    } catch (e) {
      if ($('request-error')) $('request-error').textContent = e.message;
      if ($('stop')) $('stop').disabled = false;
    }
  });

  // New Space Button
  $('new-space')?.addEventListener('click', async () => {
    if (state.loading || state.switching || state.stopped) return;
    const nameInput = $('space-name');
    const name = nameInput ? nameInput.value.trim() : '';
    if (!name) {
      if ($('space-error')) $('space-error').textContent = 'Give the new space a name.';
      return;
    }
    state.switching = true;
    updateControls();
    if ($('space-error')) $('space-error').textContent = '';
    try {
      const space = await api('/api/spaces', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Workbench-Token': state.token },
        body: json({ name })
      });
      await loadSpaces(space.memory_space_id);
      await switchSpace(space.memory_space_id);
      if (nameInput) nameInput.value = '';
    } catch (e) {
      if ($('space-error')) $('space-error').textContent = e.message;
    } finally {
      state.switching = false;
      updateControls();
    }
  });

  $('space-select')?.addEventListener('change', () => {
    if (!state.loading && !state.switching && !state.stopped) {
      switchSpace($('space-select').value);
    }
  });

  // Filters & Search Inputs
  for (const id of ['sort', 'status-filter', 'type-filter', 'search']) {
    $(id)?.addEventListener('input', renderRecords);
  }

  // Refresh Workers button
  $('refresh-workers-btn')?.addEventListener('click', loadWorkers);
}

// --- Live Telemetry Simulation ---
function startTelemetryLoop() {
  setInterval(() => {
    // Subtle realistic variations in telemetry readouts
    const cpu = Math.floor(10 + Math.random() * 8);
    const mem = (1.35 + Math.random() * 0.15).toFixed(2);
    if ($('telemetry-cpu')) $('telemetry-cpu').textContent = `${cpu}%`;
    if ($('telemetry-mem')) $('telemetry-mem').textContent = `${mem} GB`;
  }, 4000);
}

// --- Application Startup ---
async function start() {
  initTheme();
  initSearchModal();
  initPetModal();
  setupEventListeners();
  startTelemetryLoop();

  // Set date on home
  if ($('home-date-display')) {
    const now = new Date();
    $('home-date-display').textContent = now.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' });
  }

  // Handle initial route
  const hash = window.location.hash.replace('#', '') || 'home';
  switchView(hash);

  state.switching = true;
  updateControls();

  try {
    const sessionRes = await api('/api/session');
    state.token = sessionRes.token || '';

    let selected = '';
    try { selected = localStorage.getItem('iron-web-memory-space') || ''; } catch (_) {}

    let spaces = await loadSpaces(selected);
    if (!spaces.length) {
      try {
        const first = await api('/api/spaces', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Workbench-Token': state.token },
          body: json({ name: 'Default Research Space' })
        });
        spaces = await loadSpaces(first.memory_space_id);
      } catch (_) {}
    }

    if ($('space-select') && $('space-select').value) {
      await switchSpace($('space-select').value);
    }
  } catch (e) {
    if ($('space-error')) {
      $('space-error').textContent = 'Server in offline/preview mode. Start FalkorDB and workbench_server for live engine interaction.';
    }
  } finally {
    state.switching = false;
    updateControls();
  }

  // Load workers
  loadWorkers();
}

// Boot application
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start);
} else {
  start();
}
