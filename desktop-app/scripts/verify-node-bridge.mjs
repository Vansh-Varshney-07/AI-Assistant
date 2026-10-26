import { build } from 'esbuild';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const project = path.dirname(root);
const [runtime, report] = process.argv.slice(2);
assert(runtime && report, 'Runtime and report paths required');
const compiled = path.join(root, 'test-results', 'bridge-smoke.mjs');
await build({ entryPoints: [path.join(root, 'src/main/bridge.ts')], outfile: compiled, platform: 'node', format: 'esm', bundle: true });
const { BackendBridge } = await import(pathToFileURL(compiled).href);
const bridge = new BackendBridge(project, path.join(root, 'backend/host.py'), runtime);
const checks = [];
const check = (name, value) => { assert(value, name); checks.push({ name, passed: true }); };
try {
  const state = await bridge.connect(); check('node_owned_bootstrap_ready', state.state === 'ready');
  check('no_credential_in_renderer_metadata', !JSON.stringify(state).includes('Bearer'));
  const space = await bridge.call('create_space', { name: 'Synthetic Node bridge qualification' });
  check('authenticated_space_creation', typeof space.id === 'string');
  const inventory = await bridge.call('inventory', { space: space.id }); check('scoped_real_inventory', Array.isArray(inventory.records) && inventory.records.length === 0);
  await assert.rejects(bridge.call('schedule_create', {}), /not included/); check('unfinished_endpoint_denied', true);
  await assert.rejects(bridge.call('snapshot', { space: 'foreign-space' }), /unavailable/); check('foreign_space_denied', true);
  await bridge.close(); check('owned_child_shutdown_observed', bridge.state.state === 'offline');
  const result = { scope: 'actual production Node bridge + private Python process + authenticated API + disposable stores; no Electron window', checks, passed: checks.length };
  await writeFile(report, JSON.stringify(result, null, 2) + '\n'); console.log(JSON.stringify(result));
} finally { await bridge.close(); }
