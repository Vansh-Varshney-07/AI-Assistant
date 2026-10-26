// Rendered UI fixtures only: never qualifies a real provider or native action.
import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(process.env.WAYFINDER_PLAYWRIGHT_MODULE || import.meta.url);
const { chromium } = require('playwright');
const output = path.join(root, 'test-results/rendered');
await fs.mkdir(output, { recursive: true });
const renderer = path.join(root, 'dist/renderer');
const contentTypes = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.ttf': 'font/ttf' };
const server = http.createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const target = path.resolve(renderer, `.${pathname === '/' ? '/index.html' : pathname}`);
    if (!target.startsWith(`${renderer}${path.sep}`)) { res.writeHead(403).end(); return; }
    res.setHeader('Content-Type', contentTypes[path.extname(target)] || 'application/octet-stream');
    res.end(await fs.readFile(target));
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ executablePath: process.env.WAYFINDER_CHROME, headless: true });
const results = [], blocked = [], faults = [];
async function fixture(manifest) {
  const ready = { state: 'ready', capabilities: { memory: true, documents: false }, runtime: 'Synthetic UI fixture — not a live runtime' };
  const api = {
    connect: async () => ready, status: async () => ready,
    profiles: async () => ({...manifest,profiles:manifest.profiles.map(p=>({...p,execution:{included:['A01','A05','A06'].includes(p.id),available:false,status:p.id==='A08'?'deferred':'inspection_required',note:p.limitation}})),presets:manifest.presets.map(p=>({...p,available:false}))}),
    profileTasks: async () => [],
    listSpaces: async () => [{ id: 'synthetic-a', name: 'Synthetic UI fixture' }],
    getSettings: async () => ({ font_size: 14, background: false }),
    setFontSize: async size => ({ font_size: size, background: false }),
    fileSelection: async () => null, repositorySelection: async () => null,
    snapshot: async () => ({ actions: [], workflows: [], jobs: [], metrics: {} }),
    inventory: async () => ({ records: [] }),
    source: async () => ({ content: 'Synthetic long source. <img src=x onerror=alert(1)> ' + 'Long source evidence remains plain text. '.repeat(30) + 'UNBROKEN_'.repeat(50) }),
    recall: async (...args) => { window.__calls.push(['recall', ...args]); return { packet: { answer_status: 'supported', evidence: [{ value: 30, predicate: 'retention_days', accepted_for_current_use: true, memory_id: 'synthetic-source' }] } }; },
    googleStatus: async () => ({ credential_file_present: false, live_qualified: false, setup: 'Synthetic setup response. No account access.' }),
  };
  window.__calls = [];
  window.wayfinder = new Proxy(api, { get(target, key) { return key in target ? target[key] : async () => { window.__calls.push(['unsupported', key]); throw new Error(`Fixture does not implement ${String(key)}`); }; } });
}
try {
  for (const [width, height, scale] of [[1440,1000,1],[1280,800,1],[600,920,1],[1920,1080,1],[1280,800,1.25],[1280,800,1.5]]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: scale, reducedMotion: 'reduce' });
    await context.addInitScript(fixture,JSON.parse(await fs.readFile(path.join(root,'../wayfinder/platform/task-profiles.json'),'utf8')));
    const page = await context.newPage();
    page.on('pageerror', error => faults.push(error.message));
    await page.route('**/*', route => { if (new URL(route.request().url()).origin !== origin) { blocked.push(route.request().url()); return route.abort(); } return route.continue(); });
    await page.goto(origin);
    await page.getByRole('heading', { name: 'Good day, Operator.' }).waitFor();
    await page.getByRole('option', { name: 'Synthetic UI fixture', exact: true }).waitFor({ state: 'attached' });
    await page.evaluate(() => document.fonts.ready);
    assert.equal(await page.locator('textarea').isDisabled(), true);
    assert.equal(await page.evaluate(() => document.fonts.check('14px Geist')), true);
    assert.equal(await page.evaluate(() => document.fonts.check('14px "Space Grotesk"')), true);
    await page.screenshot({ path: path.join(output, `home-${width}-${scale}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Use light theme' }).click();
    assert.equal(await page.locator('.app').getAttribute('data-theme'), 'light');
    await page.screenshot({ path: path.join(output, `light-${width}-${scale}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Open command palette' }).click();
    const palette = page.getByRole('dialog', { name: 'Command palette' });
    await palette.getByRole('textbox', { name: 'Search destinations' }).fill('Memory');
    await palette.getByRole('button', { name: 'Memory' }).click();
    await page.getByLabel('Memory field').fill('retention_days');
    await page.getByRole('button', { name: 'Recall memory' }).click();
    await page.getByText('30', { exact: true }).waitFor();
    assert.deepEqual(await page.evaluate(() => window.__calls), [['recall','synthetic-a','me','retention_days','now']]);
    await page.getByRole('button', { name: 'Inspect source' }).click();
    await page.getByRole('heading', { name: 'Source record', exact: true }).waitFor();
    assert.equal(await page.locator('.source-copy').evaluate(element => getComputedStyle(element).fontSize), '14px');
    assert.equal(await page.locator('img').count(), 0);
    await page.screenshot({ path: path.join(output, `memory-${width}-${scale}.png`), fullPage: true });
    await page.keyboard.press('Control+k');
    await palette.waitFor();
    await page.keyboard.press('Escape');
    await palette.waitFor({ state: 'hidden' });
    if (width <= 900) {
      const opener = page.getByRole('button', { name: 'Open navigation' });
      await opener.click();
      const drawer = page.getByRole('dialog', { name: 'Workspace navigation' });
      await drawer.waitFor();
      for (let i=0;i<13;i++) {
        await page.keyboard.press('Tab');
        assert.equal(await drawer.evaluate(element => element.contains(document.activeElement)), true);
      }
      await page.keyboard.press('Escape');
      await drawer.waitFor({ state: 'hidden' });
      assert.equal(await opener.evaluate(element => document.activeElement === element), true);
      await opener.click(); await page.keyboard.press('Control+k');
      await palette.waitFor();
      assert.equal(await page.locator('dialog[open]').count(), 1);
      await page.keyboard.press('Escape');
      await opener.click(); await page.setViewportSize({ width: 1280, height: 800 });
      await drawer.waitFor({ state: 'hidden' });
      await page.setViewportSize({ width, height });
    }
    const overflow = await page.evaluate(() => ({ body: document.documentElement.scrollWidth > innerWidth + 1, page: document.querySelector('.page').scrollWidth > document.querySelector('.page').clientWidth + 1 }));
    assert.deepEqual(overflow, { body: false, page: false });
    await page.keyboard.press('Control+k');
    await palette.getByRole('textbox', { name: 'Search destinations' }).fill('Connections');
    await palette.getByRole('button', { name: 'Connections' }).click();
    await page.getByRole('button', { name: /Check setup/ }).click();
    await page.getByText(/Account setup required/).waitFor();
    await page.screenshot({ path: path.join(output, `connections-${width}-${scale}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Open settings' }).click();
    await page.getByLabel('Reading size').selectOption('20');
    await page.keyboard.press('Control+k');
    await palette.getByRole('textbox', { name: 'Search destinations' }).fill('Memory');
    await palette.getByRole('button', { name: 'Memory' }).click();
    await page.getByLabel('Memory field').fill('retention_days');
    await page.getByRole('button', { name: 'Recall memory' }).click();
    await page.getByRole('button', { name: 'Inspect source' }).click();
    assert.equal(await page.locator('.source-copy').evaluate(element => getComputedStyle(element).fontSize), '20px');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), true);
    await page.keyboard.press('Control+k');
    await palette.getByRole('textbox', {name:'Search destinations'}).fill('Agents');
    await palette.getByRole('button', {name:'Agents & apps'}).click();
    await page.getByRole('heading',{name:'Task profiles',exact:true}).waitFor();
    assert.equal(await page.locator('.profile-card').count(),8);
    assert.equal(await page.locator('.agents-page .connection-card').count(),6);
    await page.getByRole('button',{name:'Select A08 Fitness & Habits'}).click();
    assert.equal(await page.getByRole('button',{name:'Run selected-file task'}).count(),0);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    await page.screenshot({path:path.join(output,`agents-${width}-${scale}.png`),fullPage:true});
    results.push({ width, height, scale, tier: 'rendered-synthetic-fixture', passed: true, checks: ['local fonts','disabled unimplemented chat','theme','palette','scoped recall','long inert source','reading size applied','no overflow','setup state',...(width<=900?['drawer focus trap','Escape focus restoration','single modal','resize recovery']:[])] });
    await context.close();
  }
  assert.deepEqual(blocked, [], 'Renderer attempted a nonlocal request');
  assert.deepEqual(faults, [], 'Renderer had uncaught errors');
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify({ results, blocked, faults, caveat: 'Synthetic renderer fixtures only. Does not qualify Electron IPC, live backend, providers or native actions.' }, null, 2));
  console.log(JSON.stringify({ passed: results.length, blocked, faults, report: path.join(output, 'report.json') }));
} finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
