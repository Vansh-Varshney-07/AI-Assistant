/* Execute actual preview script with a minimal fake DOM. This is not a browser,
 * a CSS layout engine, an accessibility audit or an Electron/native app test. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.dirname(__dirname);
const html = fs.readFileSync(path.join(root, 'preview.html'), 'utf8');
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Classes {
  constructor(values = []) { this.values = new Set(values); }
  contains(k) { return this.values.has(k); }
  add(k) { this.values.add(k); }
  remove(k) { this.values.delete(k); }
  toggle(k, force) { const add = force === undefined ? !this.contains(k) : force; add ? this.add(k) : this.remove(k); return add; }
}
class Element {
  constructor() { this.innerHTML = ''; this.textContent = ''; this.dataset = {}; this.classList = new Classes(); this.listeners = {}; this.id = ''; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  closest() { return this; }
}
const nodes = new Map();
const get = s => { if (!nodes.has(s)) nodes.set(s, new Element()); return nodes.get(s); };
const tabNodes = ['plan', 'sources', 'review'].map(tab => { const e = new Element(); e.dataset.tab = tab; return e; });
const listeners = {};
const document = {
  querySelector: get,
  querySelectorAll: () => tabNodes,
  addEventListener: (type, fn) => { listeners[type] = fn; },
};
const context = vm.createContext({ document, setTimeout: () => 1, clearTimeout: () => {} });
vm.runInContext(source, context, { timeout: 3000 });
const readState = () => JSON.parse(vm.runInContext('JSON.stringify([release,page,tab])', context)).concat(get('#layout').classList.contains('show-inspector'));
const key = state => JSON.stringify(state);
function restore(state) {
  vm.runInContext(`release=${state[0]};page=${JSON.stringify(state[1])};tab=${JSON.stringify(state[2])};renderPage();renderDetails();`, context);
  get('#layout').classList.toggle('show-inspector', state[3]);
}
function click(action) {
  const e = new Element();
  if (action[0] === 'toggle') e.id = 'toggle-inspector';
  else e.dataset[action[0]] = String(action[1]);
  listeners.click({ target: e });
}
function actions() {
  const result = Array.from({ length: 7 }, (_, i) => ['release', i + 1]);
  const buttons = [...get('.nav').innerHTML.matchAll(/data-page="([^"]+)"/g)].map(m => ['page', m[1]]);
  return result.concat(buttons, [['page', 'flows'], ['tab', 'plan'], ['tab', 'sources'], ['tab', 'review'], ['toggle']]);
}
const initial = readState();
const queue = [initial], states = new Map([[key(initial), initial]]), parent = new Map([[key(initial), null]]), graph = new Map();
for (let cursor = 0; cursor < queue.length; cursor++) {
  const state = queue[cursor]; restore(state); const outgoing = [];
  for (const action of actions()) {
    restore(state); click(action); const next = readState(), id = key(next);
    outgoing.push(id);
    if (!states.has(id)) { states.set(id, next); parent.set(id, [key(state), action]); queue.push(next); }
  }
  graph.set(key(state), outgoing);
}
const dfs = new Set(), stack = [key(initial)];
while (stack.length) { const id = stack.pop(); if (dfs.has(id)) continue; dfs.add(id); stack.push(...graph.get(id)); }
assert.equal(dfs.size, states.size);
for (const id of states.keys()) assert(dfs.has(id));
const checks = [];
function check(id, actual, expected, detail) { checks.push({ id, pass: actual === expected, actual, expected, detail }); }
restore([1, 'chat', 'plan', false]);
check('P01-r1-navigation', /data-page="(tasks|scheduler|workflows|memory|connections|agents|skills)"/.test(get('.nav').innerHTML), false, 'R1 destinations should remain Chat, Runs and Settings.');
check('P02-r1-no-google-inspector', /calendar|selected tasks/i.test(get('#details').innerHTML), false, 'R1 inspector currently shows R3 sources.');
restore([2, 'chat', 'plan', false]);
check('P03-r2-no-google-prompt', /using my calendar and tasks/.test(get('#content').innerHTML), false, 'R2 scenario should use memory/documents, not unshipped Google.');
restore([1, 'chat', 'review', true]);
check('P04-r1-no-task-approval', /Proposed local task|Approve once/.test(get('#details').innerHTML), false, 'R1 exposes a task action planned for R3.');
restore([7, 'projects', 'plan', false]); click(['release', 1]);
check('P05-lower-release-navigation-reset', readState()[1], 'chat', 'Switching to R1 correctly leaves a later-release destination.');
restore([1, 'chat', 'plan', false]);
const imeEvent = { key: 'Enter', shiftKey: false, isComposing: true, prevented: false, preventDefault() { this.prevented = true; } };
get('textarea').listeners.keydown(imeEvent);
check('P06-ime-enter', imeEvent.prevented, false, 'IME composition should not be interpreted as submit.');
const normalEvent = { key: 'Enter', shiftKey: false, prevented: false, preventDefault() { this.prevented = true; } };
get('textarea').listeners.keydown(normalEvent);
check('P07-enter-preview-is-inert', /no request was sent/.test(get('#toast').textContent), true, 'Preview send only announces that nothing was sent.');
// Static CSS checks are source evidence only, not viewport render measurements.
check('P08-narrow-drawer-control', /id="toggle-sidebar"|data-action="toggle-sidebar"/.test(html), true, 'Sidebar is hidden below 760px but has no implemented reopen control.');
const desktopToggleRule = /\.layout\.hide-inspector\s+\.inspector|\.layout:not\(\.show-inspector\)\s+\.inspector/.test(html);
check('P09-wide-inspector-toggle-rule', desktopToggleRule, true, 'Current toggle class only affects a media-query sheet; wide inspector has no hide rule.');
check('P10-preview-no-network', html.includes("connect-src 'none'"), true, 'Preview declares no backend network connections.');
check('P11-composer-focus-style', /\.composer textarea\{[^}]*outline:none!important/.test(html), false, 'Composer rule overrides the declared focus-visible outline; static CSS cascade observation.');
function trace(state) { let at = key(state), result = []; while (parent.get(at)) { const entry = parent.get(at); result.push(entry[1]); at = entry[0]; } return result.reverse(); }
const report = {
  scope: 'actual inline preview JS with fake DOM; CSS observations are static only',
  reachable_states: states.size,
  transitions: [...graph.values()].reduce((sum, edges) => sum + edges.length, 0),
  bfs_dfs_same_reachable_states: true,
  actions: 'release selection, visible navigation, design flow, inspector tabs, inspector toggle',
  checks, passed: checks.filter(c => c.pass).length, failed: checks.filter(c => !c.pass).length,
  sample_shortest_trace_to_r1_review: trace([1, 'chat', 'review', true]),
  exclusions: ['real browser', 'CSS rendering', 'screen reader', 'Electron IPC', 'backend', 'provider', 'actual desktop'],
};
fs.writeFileSync(path.join(__dirname, 'preview-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
