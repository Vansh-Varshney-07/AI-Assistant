/* Actual offline-preview handlers in a fake DOM. No renderer/native/IPC proof. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const root = path.dirname(__dirname);
const targetedOnly = process.argv.includes('--targeted-only');
const html = fs.readFileSync(path.join(root, 'preview.html'), 'utf8');
const inputHashes = Object.fromEntries(['preview.html', 'preview.js', 'manifest.json'].map(name => [name, createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex')]));
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const nodes = new Map(), listeners = {}, windowListeners = {};
class Classes {
  constructor() { this.values = new Set(); }
  contains(k) { return this.values.has(k); }
  add(k) { this.values.add(k); }
  remove(k) { this.values.delete(k); }
  toggle(k, force) { const add = force === undefined ? !this.contains(k) : force; add ? this.add(k) : this.remove(k); return add; }
}
class Element {
  constructor() { this.innerHTML = ''; this.textContent = ''; this.dataset = {}; this.classList = new Classes(); this.listeners = {}; this.attributes = {}; this.id = ''; this.open = false; this.isConnected = true; this.focuses = 0; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  closest() { return this; }
  setAttribute(k, value) { this.attributes[k] = value; }
  focus() { this.focuses++; document.activeElement = this; }
  showModal() { assert(!this.open, 'Double-open modal'); this.open = true; }
  close() { this.open = false; }
}
const get = selector => { if (!nodes.has(selector)) nodes.set(selector, new Element()); return nodes.get(selector); };
const document = { querySelector: get, activeElement: null, addEventListener: (type, fn) => { listeners[type] = fn; } };
const window = { innerWidth: 1440, addEventListener: (type, fn) => { windowListeners[type] = fn; } };
const context = vm.createContext({ document, window, setTimeout: () => 1, clearTimeout: () => {} });
const evaluate = code => vm.runInContext(code, context, { timeout: 3000 });
evaluate(source);
const state = () => JSON.parse(evaluate('JSON.stringify([release,page,tab,inspectorVisible,overlay,widthBand])'));
const key = value => JSON.stringify(value);
function restore(s) {
  const width = { narrow: 600, medium: 1000, wide: 1440 }[s[5]];
  window.innerWidth = width;
  evaluate(`release=${s[0]};page=${JSON.stringify(s[1])};tab=${JSON.stringify(s[2])};inspectorVisible=${s[3]};overlay=${JSON.stringify(s[4])};widthBand=${JSON.stringify(s[5])};returnFocus=null;composing=false;renderPage();`);
  get('#navigation-dialog').open = s[4] === 'navigation'; get('#inspector-dialog').open = s[4] === 'inspector';
  get('#toggle-sidebar').setAttribute('aria-expanded', String(s[4] === 'navigation'));
}
function click(action, button = new Element()) {
  if (action[0] === 'id') button.id = action[1];
  else button.dataset[action[0]] = String(action[1]);
  listeners.click({ target: button });
  return button;
}
function act(action) {
  if (action[0] === 'width') { window.innerWidth = action[1]; windowListeners.resize(); }
  else if (action[0] === 'escape') listeners.keydown({ key: 'Escape', preventDefault() {} });
  else click(action);
}
function actions() {
  return Array.from({ length: 7 }, (_, i) => ['release', i + 1])
    .concat(JSON.parse(evaluate('JSON.stringify(allowedPages().map(d=>["page",d[0]]))')))
    .concat(JSON.parse(evaluate('JSON.stringify(allowedTabs().map(t=>["tab",t]))')))
    .concat([['id', 'toggle-sidebar'], ['id', 'toggle-inspector'], ['escape'], ['width', 600], ['width', 1000], ['width', 1440]]);
}
function invariant(s) {
  assert(evaluate('allowedPages().some(d=>d[0]===page)'));
  assert(evaluate('allowedTabs().includes(tab)'));
  if (s[4] === 'navigation') assert(!s[3]);
  if (s[4] === 'inspector') assert(s[3] && s[5] !== 'wide');
  assert.equal(Number(get('#navigation-dialog').open) + Number(get('#inspector-dialog').open) <= 1, true);
  assert.equal(get('#layout').classList.contains('inspector-visible'), s[3] && s[5] === 'wide');
  if (s[0] === 1) assert(!/calendar|local task|review example/i.test(get('#details').innerHTML));
}
const initial = state(), queue = [initial], seen = new Map([[key(initial), initial]]), graph = new Map();
for (let cursor = 0; !targetedOnly && cursor < queue.length; cursor++) {
  const current = queue[cursor]; restore(current); const edges = [];
  for (const action of actions()) {
    restore(current); act(action); const next = state(); invariant(next); const id = key(next); edges.push(id);
    if (!seen.has(id)) { seen.set(id, next); queue.push(next); }
  }
  graph.set(key(current), edges);
}
const dfs = new Set(), stack = [key(initial)];
if (targetedOnly) graph.set(key(initial), []);
while (stack.length) { const id = stack.pop(); if (dfs.has(id)) continue; dfs.add(id); stack.push(...graph.get(id)); }
assert.equal(dfs.size, seen.size); for (const id of seen.keys()) assert(dfs.has(id));
const checks = [];
const check = (id, condition, detail) => checks.push({ id, pass: Boolean(condition), detail });
check('P01-manifest-one-source', JSON.stringify(JSON.parse(evaluate('JSON.stringify(manifest)'))) === JSON.stringify(JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'))), 'Generated preview manifest equals authoritative JSON.');
restore(initial); check('P02-default-r1', state()[0] === 1, 'The smallest release is the initial example.');
check('P03-r1-navigation', !/data-page="(tasks|memory|connections|scheduler|skills)"/.test(get('.nav').innerHTML), 'R1 only exposes core destinations.');
check('P04-r1-inspector', !/calendar|local task|Review example/.test(get('#details').innerHTML), 'No later-release review/evidence in R1.');
restore([2, 'chat', 'plan', false, 'none', 'wide']);
check('P05-r2-example', !/calendar|Google/.test(get('#content').innerHTML), 'R2 chat uses selected memory/documents.');
restore(initial); click(['tab', 'review']); check('P06-deny-hidden-tab', state()[2] === 'plan', 'A direct hidden-tab intent cannot expose R2 review.');
click(['page', 'projects']); check('P07-deny-hidden-route', state()[1] === 'chat', 'Hidden later route remains unavailable.');
restore([7, 'projects', 'review', true, 'none', 'wide']); click(['release', 1]);
check('P08-downgrade-route-tab', state()[1] === 'chat' && state()[2] === 'plan', 'Lower release normalizes both route and detail tab.');
restore(initial); click(['id', 'toggle-inspector']);
check('P09-wide-inspector-open', get('#layout').classList.contains('inspector-visible') && get('#toggle-inspector').attributes['aria-expanded'] === 'true', 'Wide visibility and control agree.');
click(['id', 'toggle-inspector']); check('P10-wide-inspector-close', !get('#layout').classList.contains('inspector-visible'), 'Wide details close.');
restore([3, 'chat', 'plan', false, 'none', 'narrow']);
const opener = click(['id', 'toggle-sidebar']);
check('P11-drawer-open', get('#navigation-dialog').open && get('#drawer-nav').innerHTML.includes('data-page="tasks"'), 'Narrow navigation exposes every enabled destination.');
listeners.keydown({ key: 'Escape', preventDefault() {} });
check('P12-drawer-escape-focus', !get('#navigation-dialog').open && opener.focuses === 1, 'Escape closes drawer and requests trigger focus restore.');
click(['id', 'toggle-sidebar']); click(['id', 'toggle-inspector']);
check('P13-single-overlay', !get('#navigation-dialog').open && get('#inspector-dialog').open, 'Opening inspector replaces navigation modal.');
act(['width', 1440]); check('P14-resize-clears-overlay', state()[4] === 'none' && !get('#inspector-dialog').open, 'Crossing breakpoint closes modal without losing route/tab.');
restore([3, 'tasks', 'sources', false, 'none', 'narrow']); click(['id', 'toggle-sidebar']); click(['page', 'today']);
check('P15-drawer-route-close', state()[1] === 'today' && !get('#navigation-dialog').open, 'Navigation selects route and closes drawer.');
function keyEvent(options) { const e = { key: 'Enter', shiftKey: false, isComposing: false, keyCode: 13, prevented: false, preventDefault() { this.prevented = true; }, ...options }; get('textarea').listeners.keydown(e); return e; }
check('P16-ime-flag', !keyEvent({ isComposing: true }).prevented, 'IME flag is respected.');
get('textarea').listeners.compositionstart(); check('P17-ime-latch', !keyEvent({}).prevented, 'Composition latch protects missing event flag.'); get('textarea').listeners.compositionend();
check('P18-ime-key229', !keyEvent({ keyCode: 229 }).prevented, 'Composition key code is respected.');
check('P19-shift-enter', !keyEvent({ shiftKey: true }).prevented, 'Shift+Enter remains newline.');
check('P20-normal-enter', keyEvent({}).prevented && get('#toast').textContent.includes('no request was sent'), 'Normal Enter is inert preview submission.');
restore(initial); check('P21-r1-no-attachment', get('#attachment-control').innerHTML === '', 'R1 composer does not expose files.');
click(['release', 2]); check('P22-r2-attachment', get('#attachment-control').innerHTML.includes('Selected file example'), 'Supported-file example appears from R2.');
check('P23-visible-focus-source', !/outline\s*:\s*none\s*!important/.test(html) && html.includes('@media(forced-colors:active)'), 'Source includes visible/forced-colour focus rules; actual rendering untested.');
check('P24-wide-toggle-css', html.includes('.layout.inspector-visible .inspector{display:block}'), 'Wide inspector has a visibility rule.');
check('P25-modal-primitives', html.includes('<dialog id="navigation-dialog"') && html.includes('<dialog id="inspector-dialog"'), 'Native modal elements used; browser behaviour untested.');
check('P26-no-connection', html.includes("connect-src 'none'") && !/\b(fetch|XMLHttpRequest|WebSocket|localStorage|sessionStorage)\s*\(/.test(source), 'Offline prototype has no request/storage calls.');
restore([7, 'projects', 'review', true, 'none', 'wide']);
check('P27-no-optional-effect-example', !/Send now|Execute native|Approve Google/.test(get('#content').innerHTML + get('#details').innerHTML), 'Optional effect modules remain absent from core.');
restore(initial); const before = key(state()); click(['release', '99']);
check('P28-invalid-release', key(state()) === before, 'Out-of-range design release is rejected.');
restore([2, 'chat', 'plan', false, 'none', 'narrow']);
const ephemeral = click(['tab', 'sources']); ephemeral.isConnected = false;
const fallback = get('#toggle-inspector'); const beforeFallback = fallback.focuses;
listeners.keydown({ key: 'Escape', preventDefault() {} });
check('P29-detached-trigger-fallback', fallback.focuses === beforeFallback + 1, 'A removed trigger needs a live fallback focus target.');
restore([2, 'chat', 'plan', true, 'none', 'wide']);
const tabTarget = get('#wide-tabs [data-tab="sources"]'); const beforeTabFocus = tabTarget.focuses;
click(['tab', 'sources']);
check('P30-tab-rerender-focus', tabTarget.focuses === beforeTabFocus + 1, 'Rebuilt inspector buttons need selected-button focus, rather than body focus loss.');
restore([3, 'tasks', 'sources', false, 'none', 'narrow']); click(['id', 'toggle-inspector']); act(['width', 1440]);
check('P31-resize-preserves-context', state()[1] === 'tasks' && state()[2] === 'sources', 'Responsive modal close preserves route and selected detail.');
const report = { scope: 'actual offline preview JS in fake DOM; CSS source observations only', input_sha256: inputHashes, graph_executed: !targetedOnly, reachable_states: targetedOnly ? null : seen.size, transitions: targetedOnly ? null : [...graph.values()].reduce((n, e) => n + e.length, 0), bfs_dfs_agree: targetedOnly ? null : true, exhaustive_invariants: 'valid release route/tab, one overlay, wide visibility, no R1 later evidence', checks, passed: checks.filter(c => c.pass).length, failed: checks.filter(c => !c.pass).length, excluded: ['real browser rendering', 'screen reader', 'OS focus/IME', 'Electron IPC', 'backend', 'model/provider', 'native desktop'] };
fs.writeFileSync(path.join(__dirname, targetedOnly ? 'preview-targeted.json' : 'preview-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ ...report, checks: undefined }));
assert.equal(report.failed, 0, 'Preview checks failed; inspect report, do not relabel as pass');
