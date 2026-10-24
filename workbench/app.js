'use strict';
const $ = id => document.getElementById(id);
const state = {records: [], history: [], session: crypto.randomUUID(), token: '', loading: false, switching: false, stopped: false, space: ''};
function updateControls() {
  for (const id of ['send','fresh','stop','space-select','new-space']) $(id).disabled = state.loading || state.switching || state.stopped;
}
const json = value => JSON.stringify(value, null, 2);
const display = value => JSON.stringify(value, (_key, item) => item === null ? 'Unavailable' : item, 2);
const time = value => value == null ? 'Unavailable' : new Date(value * 1000).toLocaleString();
const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
async function api(path, options) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok && !body.diagnostics) throw new Error(body.error || `HTTP ${response.status}`);
  return body;
}
function filters(id, values, label) {
  const old = $(id).value;
  $(id).replaceChildren(new Option(label, ''), ...[...new Set(values)].sort().map(v => new Option(v, v)));
  if ([...$(id).options].some(o => o.value === old)) $(id).value = old;
}
function renderRecords() {
  const term = $('search').value.toLowerCase();
  const records = state.records.filter(r => r.memory_space_id === state.space &&
    (!term || json(r).toLowerCase().includes(term)) &&
    (!$('status-filter').value || (r.statuses.length ? r.statuses : ['Unavailable']).includes($('status-filter').value)) &&
    (!$('type-filter').value || (r.types.length ? r.types : ['Unavailable']).includes($('type-filter').value)));
  const [field, order] = $('sort').value.split('-');
  records.sort((a, b) => { const av = a[field + '_timestamp'], bv = b[field + '_timestamp'];
    if (av == null) return bv == null ? a.memory_id.localeCompare(b.memory_id) : 1;
    if (bv == null) return -1; return (av - bv) * (order === 'asc' ? 1 : -1) || a.memory_id.localeCompare(b.memory_id); });
  $('inventory-count').textContent = `${records.length} shown / ${state.records.length} records in this memory space. Update timestamps: Unavailable.`;
  $('records').replaceChildren();
  if (!records.length) $('records').append(el('p', 'No records match these filters.', 'muted'));
  for (const r of records) {
    const card = el('div', undefined, 'card');
    card.append(el('p', r.memory_id, 'record-title'), el('p', r.content));
    card.append(el('span', r.statuses.join(', ') || 'Status: Unavailable', 'tag'), el('span', r.types.join(', ') || 'Type: Unavailable', 'tag'));
    card.append(el('p', `Created: ${time(r.created_timestamp)} · Updated: ${time(r.updated_timestamp)}`, 'muted'));
    card.append(el('p', `Qdrant: ${r.vector_stored ? 'present' : 'missing'} · FalkorDB: ${r.graph_stored ? 'present' : 'missing'}`, 'muted'));
    const button = el('button', 'Inspect record'); button.type = 'button';
    button.onclick = () => { $('detail').textContent = display(r); };
    card.append(button); $('records').append(card);
  }
}
async function refresh() {
  const space = state.space;
  if (!space) return;
  $('refresh').disabled = true; $('inventory-error').textContent = '';
  try {
    const [status, inventory] = await Promise.all([api('/api/status'), api('/api/memories?memory_space_id=' + encodeURIComponent(space))]);
    if (space !== state.space) return;
    $('status').textContent = display(status); state.records = inventory.records;
    const selectedModel = $('model').value;
    $('model').replaceChildren(new Option('Evidence only · no hosted calls',''),...(status.models || []).map(m=>new Option(m,m)));
    $('model').value = selectedModel;
    filters('status-filter', state.records.flatMap(r => r.statuses.length ? r.statuses : ['Unavailable']), 'All statuses');
    filters('type-filter', state.records.flatMap(r => r.types.length ? r.types : ['Unavailable']), 'All types');
    if (inventory.unowned_observation_ids.length) $('inventory-error').textContent = `Unowned observations (not omitted silently): ${inventory.unowned_observation_ids.join(', ')}`;
    renderRecords();
  } catch (e) { if (space === state.space) $('inventory-error').textContent = `Refresh failed: ${e.message}. Any displayed records are from the last successful refresh.`; }
  finally { $('refresh').disabled = false; }
}
function selectRequest(entry) {
  $('retrieved').replaceChildren();
  const {result} = entry;
  if (result.recall) $('retrieved').append(el('pre', display(result.recall)));
  else if (!result.retrieved.length) $('retrieved').append(el('p', 'No memories returned for this request.', 'muted'));
  else for (const hit of result.retrieved) {
    const d = el('details'); d.append(el('summary', `${hit.memory_id} · score ${hit.score}`), el('pre', display(hit))); $('retrieved').append(d);
  }
}
function renderHistory() {
  $('history').replaceChildren();
  for (const entry of state.history.filter(e => e.memory_space_id === state.space)) {
    const card = el('div', undefined, 'card');
    card.append(el('p', `${entry.mode} · ${entry.memory_space_id}`, 'muted'), el('p', entry.prompt));
    card.append(el('p', entry.model || 'Evidence only', 'muted'));
    const d = entry.result.diagnostics;
    card.append(el('p', `Memory pipeline: ${d.pipeline_invoked ? 'invoked' : 'not invoked'} · ${entry.result.ok ? 'completed' : 'failed'}`, 'tag'));
    if (entry.result.assistant) {
      card.append(el('p', entry.result.assistant.answer));
      card.append(el('p', `Evidence status: ${entry.result.assistant.evidence_status}`, 'tag'));
      for (const id of entry.result.assistant.citations) {
        const source = el('button', `Source ${id}`); source.type = 'button';
        source.onclick = () => { const record=state.records.find(r=>r.memory_id===id); $('detail').textContent=record?display(record):'Source not in the last inventory refresh.'; };
        card.append(source);
      }
    }
    // Render only values supplied by the engine. Do not synthesize an assistant answer.
    if (entry.result.recall) card.append(el('pre', display(entry.result.recall)));
    else card.append(el('pre', display({retrieved: entry.result.retrieved.map(h => ({memory_id: h.memory_id, content: h.content, score: h.score})), stored_memory_id: entry.result.stored?.memory_id ?? null})));
    const details = el('details'); details.append(el('summary', 'Execution diagnostics'), el('pre', display(d))); card.append(details);
    const select = el('button', 'Show retrieved records'); select.type = 'button'; select.onclick = () => selectRequest(entry); card.append(select);
    const download = el('button', 'Save request evidence'); download.type = 'button';
    download.onclick = () => { const url = URL.createObjectURL(new Blob([json(entry)], {type:'application/json'})); const a = el('a'); a.href = url; a.download = `memory-evidence-${entry.request_id}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }; card.append(download);
    $('history').append(card);
  }
  $('history').scrollTop = $('history').scrollHeight;
}
$('prompt-form').addEventListener('submit', async event => {
  event.preventDefault(); if (state.loading || state.switching || state.stopped) return;
  if (!state.space) { $('request-error').textContent = 'Create or select a memory space first.'; return; }
  $('request-error').textContent = ''; state.loading = true;
  $('send').disabled = true; $('fresh').disabled = true; $('stop').disabled = true; $('activity').textContent = 'Running the memory engine…';
  $('space-select').disabled = true; $('new-space').disabled = true;
  try {
    const body = {prompt: $('prompt').value, mode: $('mode').value, memory_space_id: state.space,
      session_id: state.session, request_id: crypto.randomUUID(), subject: $('subject').value,
      predicate: $('predicate').value, confirmed: $('confirmed').checked,
      top_k: Number($('top-k').value), temporal_mode: $('temporal').value, model:$('model').value};
    if (body.mode === 'claim') body.claims = JSON.parse($('claims').value, (_key,value)=>{
      if (typeof value==='number' && Number.isInteger(value) && !Number.isSafeInteger(value)) throw new Error('Claim JSON contains an unsafe large integer. Omit unbounded validity fields to use the exact engine defaults.');
      return value;
    });
    const result = await api('/api/prompt', {method:'POST', headers:{'Content-Type':'application/json', 'X-Workbench-Token':state.token}, body:json(body)});
    const entry = {...body, submitted_at:new Date().toISOString(), result}; state.history.push(entry);
    renderHistory(); selectRequest(entry);
    if (!result.ok) $('request-error').textContent = json(result.diagnostics.errors);
    else $('prompt').value = '';
    await refresh();
  } catch (e) { $('request-error').textContent = e.message + ' No completion is asserted. Inspect storage before resubmitting a failed write.'; }
  finally { state.loading = false; updateControls(); $('activity').textContent = ''; }
});
$('mode').onchange = () => { $('claim-controls').hidden = $('mode').value !== 'claim'; };
$('fresh').onclick = () => { state.history = state.history.filter(e => e.memory_space_id !== state.space); state.session = crypto.randomUUID(); $('history').replaceChildren(el('p', 'Fresh conversation. This space’s long-term memories are preserved.', 'muted')); $('retrieved').textContent = 'Unavailable — send a prompt.'; $('prompt').value = ''; $('request-error').textContent = ''; };
$('refresh').onclick = refresh;
$('stop').onclick = async () => {
  $('stop').disabled = true;
  try {
    await api('/api/stop', {method:'POST', headers:{'Content-Type':'application/json', 'X-Workbench-Token':state.token}, body:'{}'});
    state.stopped = true; updateControls(); $('refresh').disabled = true;
    $('activity').textContent = 'Workbench stopping cleanly. Restart with the documented PowerShell commands, then reload this page.';
  } catch(e) { $('request-error').textContent = e.message; $('stop').disabled = false; }
};
for (const id of ['sort','status-filter','type-filter','search']) $(id).addEventListener('input', renderRecords);
async function loadSpaces(selected) {
  const {spaces} = await api('/api/spaces');
  $('space-select').replaceChildren(...spaces.map(s => new Option(`${s.name} · ${s.memory_space_id}`, s.memory_space_id)));
  if (spaces.some(s => s.memory_space_id === selected)) $('space-select').value = selected;
  return spaces;
}
async function switchSpace(id) {
  state.switching = true; updateControls();
  state.space = id; state.records = []; state.session = crypto.randomUUID();
  try { localStorage.setItem('iron-web-memory-space', id); } catch (_) { /* Optional preference only. */ }
  $('active-space').textContent = `Active memory space ID: ${id}`;
  $('detail').textContent = 'Select a stored record in this space.';
  $('retrieved').textContent = 'Unavailable — send a prompt in this space.';
  $('prompt').value = ''; $('claims').value = ''; $('confirmed').checked = false;
  $('subject').value = 'manual-user'; $('predicate').value = ''; $('request-error').textContent = '';
  $('search').value = ''; $('status-filter').value = ''; $('type-filter').value = '';
  try { renderHistory(); renderRecords(); await refresh(); }
  finally { state.switching = false; updateControls(); }
}
$('space-select').onchange = () => { if (!state.loading && !state.switching && !state.stopped) switchSpace($('space-select').value); };
$('new-space').onclick = async () => {
  if (state.loading || state.switching || state.stopped) return;
  state.switching = true; updateControls(); $('space-error').textContent = '';
  try {
    const name = $('space-name').value.trim();
    if (!name) throw new Error('Give the new test a name.');
    const space = await api('/api/spaces', {method:'POST', headers:{'Content-Type':'application/json', 'X-Workbench-Token':state.token}, body:json({name})});
    await loadSpaces(space.memory_space_id); await switchSpace(space.memory_space_id); $('space-name').value = '';
  } catch(e) { $('space-error').textContent = e.message; }
  finally { state.switching = false; updateControls(); }
};
async function start() {
  state.switching = true; updateControls();
  try {
    state.token = (await api('/api/session')).token;
    let selected = ''; try { selected = localStorage.getItem('iron-web-memory-space') || ''; } catch (_) { /* Optional preference only. */ }
    let spaces = await loadSpaces(selected);
    if (!spaces.length) {
      const first = await api('/api/spaces', {method:'POST', headers:{'Content-Type':'application/json', 'X-Workbench-Token':state.token}, body:json({name:'My first test'})});
      spaces = await loadSpaces(first.memory_space_id);
    }
    await switchSpace($('space-select').value);
  } catch(e) { $('space-error').textContent = e.message; }
  finally { state.switching = false; updateControls(); }
}
start();
