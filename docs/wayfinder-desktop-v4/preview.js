/* Offline design only. Content is fixed synthetic text; no requests or storage. */
const $ = selector => document.querySelector(selector);
const releases = [
  ['Real conversation', 'Actual bounded model replies, stop and reopen; no tools or implicit memory.'],
  ['Memory and documents', 'Explicit scoped memory changes and selected supported files.'],
  ['Today and local tasks', 'Google reads; local work items stay separate from provider tasks.'],
  ['Repeatable reads', 'Small versioned linear workflows, with bounded inputs and partial outcomes.'],
  ['Daily brief and quick access', 'Fixed-zone read schedule and another view on the same conversation.'],
  ['Skills and roles', 'Actual bindings, tested versions and reviewed configuration.'],
  ['Project review', 'Scoped read-only repository evidence; effects remain optional and disabled.'],
];
const destinations = [
  ['chat', 'Chat', 'chat'], ['runs', 'Runs', 'runtime'],
  ['memory', 'Memory', 'memory'], ['today', 'Today', 'google_read'],
  ['tasks', 'Local tasks', 'local_tasks'], ['connections', 'Connections', 'google_read'],
  ['workflows', 'Workflows', 'workflows'], ['scheduler', 'Scheduler', 'scheduler'],
  ['skills', 'Skills', 'skills'], ['agents', 'Agents', 'agents'],
  ['projects', 'Projects', 'project_review'], ['settings', 'Settings', 'runtime'],
];
let release = 1, page = 'chat', tab = 'plan', inspectorVisible = false;
let overlay = 'none', returnFocus = null, composing = false, toastTimer;
let widthBand = window.innerWidth <= 760 ? 'narrow' : window.innerWidth <= 1200 ? 'medium' : 'wide';
function allowedFeature(id) { return manifest.features.some(f => f.id === id && f.release <= release); }
function allowedPages() { return destinations.filter(d => allowedFeature(d[2])); }
function allowedTabs() { return release >= 2 ? ['plan', 'sources', 'review'] : ['plan']; }
function notify(message = 'Design preview only — no request was sent and nothing was changed.') {
  $('#toast').textContent = message; $('#toast').classList.remove('hidden');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => $('#toast').classList.add('hidden'), 4500);
}
function closeOverlay(restoreFocus = true) {
  const previousOverlay = overlay;
  for (const id of ['navigation-dialog', 'inspector-dialog']) {
    const dialog = $(`#${id}`); if (dialog.open) dialog.close();
  }
  if (overlay === 'inspector') inspectorVisible = false;
  overlay = 'none'; $('#toggle-sidebar').setAttribute('aria-expanded', 'false');
  if (restoreFocus && previousOverlay !== 'none') {
    const fallback = previousOverlay === 'navigation' ? $('#toggle-sidebar') : $('#toggle-inspector');
    (returnFocus?.isConnected ? returnFocus : fallback).focus();
  }
  returnFocus = null;
}
function openOverlay(kind, trigger) {
  closeOverlay(false); returnFocus = trigger || document.activeElement;
  overlay = kind; if (kind === 'inspector') inspectorVisible = true;
  $(`#${kind === 'navigation' ? 'navigation' : 'inspector'}-dialog`).showModal();
  $('#toggle-sidebar').setAttribute('aria-expanded', String(kind === 'navigation'));
}
function toggleInspector(trigger) {
  if (inspectorVisible) { closeOverlay(); inspectorVisible = false; }
  else if (widthBand === 'wide') { closeOverlay(false); inspectorVisible = true; }
  else openOverlay('inspector', trigger);
  renderInspector();
}
function summary() { return `<div class="summary"><strong>R${release} · ${releases[release - 1][0]}</strong><div>${releases[release - 1][1]}</div><div class="hint">Proposed release · synthetic design · unqualified runtime</div></div>`; }
function navigationMarkup() { return allowedPages().map(d => `<button data-page="${d[0]}" aria-current="${page === d[0] ? 'page' : 'false'}">${d[1]}</button>`).join(''); }
function chat() {
  const prompt = release === 1 ? 'Explain this project in three sentences.' : release === 2 ? 'Compare my retained preference with this selected text file.' : 'Prepare a brief from my permitted calendar and task reads.';
  const heading = release === 1 ? 'A real conversation is the first useful app.' : release === 2 ? 'Evidence, with its source and limits.' : 'A useful brief, with observation times.';
  const body = release === 1 ? 'The real R1 app must return an actual Hermes-backed answer. This offline layout does not generate one.' : release === 2 ? 'An example memory/document result belongs here. A discrepancy stays visible until a reviewed correction. No account integration is present at this release.' : 'This fictional brief represents read-only provider evidence. A local work item is independent; no provider update or synchronization is implied.';
  return summary() + `<div class="user">${prompt}</div><article class="answer"><h2>${heading}</h2><p>${body}</p><div class="card"><h3>${release === 1 ? 'Run summary' : 'Evidence and outcome'}</h3><p>${release === 1 ? 'One bounded request, durable acceptance and honest stop/recovery states.' : 'Source identity, observed version and actual coverage appear in details.'}</p><p class="hint">Synthetic example; not a completed run.</p></div><div class="actions"><button data-tab="plan">Run details</button>${release >= 2 ? '<button data-tab="sources">Sources</button><button data-tab="review">Example review</button>' : ''}${allowedFeature('workflows') ? '<button data-page="workflows">Workflow example</button>' : ''}</div></article>`;
}
const pageData = {
  runs: ['Runs', 'Canonical outcomes survive reconnect; it never repeats execution.', ['Example read attempt · not actually run', 'Interrupted request · observation only']],
  memory: ['Memory', 'Current, historical and disputed evidence stay distinct.', ['Remember / correct / retract', 'Forget barrier · fresh chat required']],
  today: ['Today', 'Permitted provider reads have separate observation times.', ['Calendar events · synthetic', 'Provider tasks · read-only', 'Gmail references · no bodies or sends']],
  tasks: ['Local tasks', 'Local tasks are independent of provider tasks.', ['Create a local work item', 'Copy to local is a one-time draft; no sync']],
  connections: ['Connections', 'Authentication, qualification and resource access are separate.', ['Google Calendar / Tasks · not connected', 'Gmail references only · not connected', 'Disable / disconnect / revoke have distinct meanings']],
  workflows: ['Workflows', 'Linear reads with frozen versions and explicit required inputs.', ['1. Calendar read', '2. Tasks read', '3. Scoped brief synthesis']],
  scheduler: ['Scheduler', 'Existing scheduler adapter must qualify before recurrence.', ['Daily read brief · draft only', 'Fixed IANA zone · skip missed/gap; first repeated time', 'Background off · no external writes']],
  skills: ['Skills', 'Review versions and effective permissions before publication.', ['Inspect installed version and fixture evidence', 'Rollback changes future configuration, not past effects']],
  agents: ['Agents', 'Logical worker roles, not permanent processes or permission grants.', ['Actual binding and effective tools', 'Unresolved numbered roles stay unavailable', 'Native execution remains disabled']],
  projects: ['Projects', 'Read-only qualified repository evidence.', ['Select a permitted repository', 'Inspect actual status/diff only after qualification', 'No command execution or write implied']],
  settings: ['Settings', 'Simple choices, honest component health and private credentials.', ['Selected provider/model · unverified here', 'Runtime / storage / model health', 'Privacy / appearance / compatibility']],
};
function renderPage() {
  if (!allowedPages().some(d => d[0] === page)) page = 'chat';
  if (!allowedTabs().includes(tab)) tab = 'plan';
  $('.release-picker').innerHTML = releases.map((r, i) => `<button data-release="${i + 1}" aria-pressed="${release === i + 1}">R${i + 1}</button>`).join('');
  $('.nav').innerHTML = navigationMarkup(); $('#drawer-nav').innerHTML = navigationMarkup();
  $('#release-caption').textContent = `R${release}: ${releases[release - 1][0]} · Every prior feature remains part of later core releases · No acceptance has run`;
  if (page === 'chat') { $('#page-title').textContent = 'Conversation'; $('#content').innerHTML = chat(); }
  else { const data = pageData[page]; $('#page-title').textContent = data[0]; $('#content').innerHTML = summary() + `<article class="answer"><h2>${data[0]}</h2><p>${data[1]}</p>${data[2].map(text => `<div class="card"><h3>${text}</h3><p class="hint">Synthetic design state · no connected runtime</p></div>`).join('')}</article>`; }
  $('#attachment-control').innerHTML = allowedFeature('documents') ? '<button data-demo="attach">＋ Selected file example</button>' : '';
  renderInspector();
}
function renderInspector() {
  if (!allowedTabs().includes(tab)) tab = 'plan';
  const titles = { plan: release === 1 ? 'Run' : 'Plan', sources: 'Sources', review: 'Review' };
  const tabs = allowedTabs().map(t => `<button data-tab="${t}" aria-pressed="${t === tab}">${titles[t]}</button>`).join('');
  $('#wide-tabs').innerHTML = tabs; $('#sheet-tabs').innerHTML = tabs;
  let detail;
  if (tab === 'plan') detail = release === 1 ? '<div class="card"><h3>Bounded chat run</h3><p>Queued → running → completed, stopped or interrupted.</p><p>Tools closed. No implicit memory.</p></div>' : release === 2 ? '<div class="card"><h3>Selected memory and document evidence</h3><p>Read permitted evidence → compare → propose a scoped correction.</p></div>' : '<div class="card"><h3>Read-only brief</h3><p>Read selected calendar and tasks → synthesize with source times.</p><p>No provider write.</p></div>';
  else if (tab === 'sources') detail = release === 2 ? '<div class="card"><h3>Evidence</h3><p>Authorized memory claim and selected text file, with versions and expiry.</p></div>' : '<div class="card"><h3>Evidence</h3><p>Authorized calendar/task projections with observation times.</p><p>Historical excerpts are distinct from fresh reads.</p></div>';
  else detail = release === 2 ? '<div class="card"><h3>Example memory correction</h3><p>Synthetic target: selected personal space / retention preference.</p><p>Proposed 30 → 42 days. Actual app must show exact service-issued digest, scope and expiry.</p><div class="actions"><button data-demo="reject">Reject example</button><button data-demo="approve">Review example only</button></div></div>' : '<div class="card"><h3>Proposed local task</h3><p>Title: Review the brief. Target: local personal task list.</p><p>No provider task change. Actual review binds exact payload/version/expiry.</p><div class="actions"><button data-demo="reject">Reject example</button><button data-demo="approve">Review example only</button></div></div>';
  $('#details').innerHTML = detail; $('#sheet-details').innerHTML = detail;
  $('#layout').classList.toggle('inspector-visible', inspectorVisible && widthBand === 'wide');
  $('#toggle-inspector').textContent = inspectorVisible ? 'Close details' : 'Open details';
  $('#toggle-inspector').setAttribute('aria-expanded', String(inspectorVisible));
  $('#toggle-inspector').setAttribute('aria-controls', widthBand === 'wide' ? 'inspector-panel' : 'inspector-dialog');
}
document.addEventListener('click', event => {
  const b = event.target.closest('button'); if (!b) return;
  if (b.dataset.release) {
    const value = Number(b.dataset.release); if (!Number.isInteger(value) || value < 1 || value > 7) return;
    closeOverlay(); release = value; renderPage();
  } else if (b.dataset.page) {
    if (!allowedPages().some(d => d[0] === b.dataset.page)) { notify('This destination is outside the selected release. Nothing was changed.'); return; }
    closeOverlay(); page = b.dataset.page; renderPage();
  } else if (b.dataset.tab) {
    if (!allowedTabs().includes(b.dataset.tab)) { notify('This detail is outside the selected release. Nothing was changed.'); return; }
    tab = b.dataset.tab; if (!inspectorVisible) toggleInspector(b); else renderInspector();
    const panel = widthBand === 'wide' ? '#wide-tabs' : '#sheet-tabs';
    $(`${panel} [data-tab="${tab}"]`)?.focus();
  } else if (b.id === 'toggle-inspector' || b.dataset.action === 'close-inspector') {
    toggleInspector(b);
  } else if (b.id === 'toggle-sidebar') {
    if (overlay === 'navigation') closeOverlay(); else { inspectorVisible = false; openOverlay('navigation', b); }
    renderInspector();
  } else if (b.dataset.action === 'close-overlay') { closeOverlay(); renderInspector(); }
  else if (b.dataset.demo || b.id === 'preview-send') notify();
});
for (const id of ['navigation-dialog', 'inspector-dialog']) $(`#${id}`).addEventListener('cancel', event => { event.preventDefault(); closeOverlay(); renderInspector(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && overlay !== 'none') { event.preventDefault(); closeOverlay(); renderInspector(); } });
$('textarea').addEventListener('compositionstart', () => { composing = true; });
$('textarea').addEventListener('compositionend', () => { composing = false; });
$('textarea').addEventListener('keydown', event => {
  if (composing || event.isComposing || event.keyCode === 229) return;
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); notify(); }
});
window.addEventListener('resize', () => {
  const next = window.innerWidth <= 760 ? 'narrow' : window.innerWidth <= 1200 ? 'medium' : 'wide';
  if (next !== widthBand) { closeOverlay(); inspectorVisible = false; widthBand = next; renderInspector(); }
});
renderPage();
