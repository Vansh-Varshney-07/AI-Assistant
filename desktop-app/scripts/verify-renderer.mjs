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
function contrast(a,b){
  const luminance=hex=>{let raw=hex.trim().replace('#','');if(raw.length===3)raw=[...raw].map(c=>c+c).join('');const c=raw.match(/../g).map(value=>parseInt(value,16)/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2];};
  const values=[luminance(a),luminance(b)].sort((x,y)=>y-x);return (values[0]+.05)/(values[1]+.05);
}
async function checkColors(page){
  const tokens=await page.locator('.app').evaluate(node=>Object.fromEntries(['--text','--muted','--primary','--knowledge','--agent','--success','--attention','--surface','--panel','--accent-solid','--accent-text'].map(name=>[name,getComputedStyle(node).getPropertyValue(name)])));
  for(const name of ['--text','--muted','--primary','--knowledge','--agent','--success','--attention'])assert(contrast(tokens[name],tokens['--surface'])>=4.5,`Insufficient text contrast: ${name}`);
  assert(contrast(tokens['--accent-text'],tokens['--accent-solid'])>=4.5,'Primary button contrast');
  const controls=await page.locator('button.primary:not(:disabled)').evaluateAll(nodes=>nodes.map(node=>({label:node.getAttribute('aria-label')||node.textContent,foreground:getComputedStyle(node).color,background:getComputedStyle(node).backgroundColor})));
  const rgbHex=value=>'#'+value.match(/[\d.]+/g).slice(0,3).map(v=>Math.round(Number(v)).toString(16).padStart(2,'0')).join('');
  for(const control of controls)assert(contrast(rgbHex(control.foreground),rgbHex(control.background))>=4.5,`Rendered primary contrast: ${control.label}`);
  const unnamed=await page.getByRole('button').evaluateAll(nodes=>nodes.filter(node=>!node.textContent.trim()&&!node.getAttribute('aria-label')).length);
  assert.equal(unnamed,0,'Unlabelled icon button');
}
async function capture(page,options){await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot(options);}
async function fixture(manifest) {
  const ready = { state: 'ready', capabilities: { memory: true, documents: false }, runtime: 'Synthetic UI fixture — not a live runtime' };
  let workflowRuns=[];
  let messages=[],setupComplete=location.search!=='?setup';
  let setupState={databaseReady:false,memoryReady:false,modelReady:false,storage:'Isolated synthetic workspace — no real files'};
  const api = {
    connect: async () => setupComplete?ready:{state:'setup'}, status: async () => setupComplete?ready:{state:'setup'},
    setupStatus:async()=>setupState,
    setupDatabase:async()=>{setupState={...setupState,databaseReady:true};return setupState;},
    setupMemory:async()=>{setupState={...setupState,memoryReady:true};return setupState;},
    setupModel:async()=>{setupState={...setupState,modelReady:true,modelExpiresAt:Date.now()+300000,model:{model:'nvidia/nemotron-3.5-lightning-30b-a3b',provider:'custom',endpoint:'integrate.api.nvidia.com'}};return setupState;},
    setupFinish:async()=>{setupComplete=true;return ready;},
    chats: async () => [{id:'synthetic-conversation',title:'A clearer plan'}],
    chat: async () => ({turns:messages}),
    newChat: async () => ({id:'synthetic-conversation',title:'New conversation'}),
    sendChat: async (_space,_conversation,_request,text) => { messages=[{id:'synthetic-turn',user_text:text,status:'completed',assistant_text:'## A manageable next step\n\nStart with one outcome and two concrete actions.\n\n| Step | Purpose |\n| --- | --- |\n| Gather context | Understand the task |\n| Choose an action | Make progress |\n\n```text\nContext → decision → next step\n```\n\n![Untrusted image](https://example.com/pixel)'}];return {turns:messages}; },
    connectionsStatus: async () => ({configured:{google:true,tavily:true,notion:true},checks:{}}),
    checkConnection: async () => ({configured:{google:true,tavily:true,notion:true},checks:{google:{passed:true,expires:Date.now()/1000+300,label:'Synthetic read check'}}}),
    googleGrant: async () => ({id:'synthetic-grant'}),
    googleRead: async () => ({records:[{id:'synthetic-event',summary:'Synthetic planning session',start:{dateTime:'2026-10-27T10:00:00Z'},end:{dateTime:'2026-10-27T10:30:00Z'}}]}),
    googleRevoke: async () => ({revoked:true}),
    profiles: async () => ({...manifest,profiles:manifest.profiles.map(p=>({...p,execution:{included:['A01','A05','A06'].includes(p.id),available:false,status:p.id==='A08'?'deferred':'inspection_required',note:p.limitation}})),presets:manifest.presets.map(p=>({...p,available:false}))}),
    workflows:async()=>workflowRuns,
    selectFiles:async()=>({grant:{id:'synthetic-grant'},files:[{id:'synthetic-file',name:'synthetic-note.md',bytes:128}]}),
    startWorkflow:async(_space,definition)=>{const result={id:'synthetic-workflow',status:'completed',definition,digest:'a'.repeat(64),events:[{status:'completed',at:1}],metrics:{worker_invocations:definition.nodes.length},nodes:definition.nodes.map(n=>({id:n.id,status:'completed',output:{text:'## Synthetic step result\n\nOnly selected fixture evidence was used.',source:{name:'synthetic-note.md',sha256:'b'.repeat(64)}}}))};workflowRuns=[result];return result;},
    workflow:async()=>workflowRuns[0],
    cancelWorkflow:async()=>({...workflowRuns[0],status:'cancelled'}),
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
  try{localStorage.setItem('wayfinder-theme','dark');}catch{/* Initial about:blank has an opaque origin. */}
  window.__calls = [];
  window.wayfinder = new Proxy(api, { get(target, key) { return key in target ? target[key] : async () => { window.__calls.push(['unsupported', key]); throw new Error(`Fixture does not implement ${String(key)}`); }; } });
}
try {
  for (const [width, height, scale] of [[1440,1000,1],[1280,800,1],[900,1000,1],[600,600,1],[900,700,1],[1920,1080,1],[1280,800,1.25],[1280,800,1.5]]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: scale, reducedMotion: 'reduce' });
    await context.addInitScript(fixture,JSON.parse(await fs.readFile(path.join(root,'../wayfinder/platform/task-profiles.json'),'utf8')));
    const page = await context.newPage();
    page.on('pageerror', error => faults.push(error.message));
    await page.route('**/*', route => { if (new URL(route.request().url()).origin !== origin) { blocked.push(route.request().url()); return route.abort(); } return route.continue(); });
    await page.goto(origin);
    await page.getByRole('heading', { name: 'A clearer plan', exact:true }).waitFor();
    await page.keyboard.press('Control+k');
    await page.getByRole('dialog',{name:'Command palette'}).getByRole('button',{name:/^Home/}).click();
    await page.getByRole('heading', { name: 'A little clarity for your day.' }).waitFor();
    await page.getByRole('option', { name: 'Synthetic UI fixture', exact: true }).waitFor({ state: 'attached' });
    await page.evaluate(() => document.fonts.ready);
    await checkColors(page);
    assert.equal(await page.getByRole('button',{name:'Open chat'}).isEnabled(), true);
    assert.equal(await page.evaluate(() => document.fonts.check('14px Geist')), true);
    assert.equal(await page.evaluate(() => document.fonts.check('14px "Space Grotesk"')), true);
    await capture(page,{ path: path.join(output, `home-${width}-${scale}.png`), fullPage: true });
    await page.getByRole('button', { name: 'Use light theme' }).click();
    assert.equal(await page.locator('.app').getAttribute('data-theme'), 'light');
    await checkColors(page);
    await capture(page,{ path: path.join(output, `light-${width}-${scale}.png`), fullPage: true });
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
    await capture(page,{ path: path.join(output, `memory-${width}-${scale}.png`), fullPage: true });
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
    await page.getByRole('button', { name: 'Check Google connection' }).click();
    await page.getByText('Live check passed',{exact:true}).waitFor();
    await page.getByRole('button', {name:'Read selected Google source'}).click();
    await page.getByText('Synthetic planning session',{exact:true}).waitFor();
    await capture(page,{ path: path.join(output, `connections-${width}-${scale}.png`), fullPage: true });
    await page.keyboard.press('Control+k');
    await palette.getByRole('textbox',{name:'Search destinations'}).fill('Chat');
    await palette.getByRole('button',{name:/^Chat/}).click();
    const message=page.getByRole('textbox',{name:'Message'});
    await message.fill('Help me make a manageable plan.');await message.press('Enter');
    await page.getByRole('heading',{name:'A manageable next step'}).waitFor();
    assert.equal(await page.locator('img').count(),0);
    assert.equal(await page.locator('.markdown table').count(),1);
    const bounds=await message.boundingBox();assert(bounds&&bounds.y>=0&&bounds.y+bounds.height<=height,'Composer must remain in viewport');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollHeight<=innerHeight+1),true,'No outer chat scroll');
    await message.fill('A draft that survives navigation');
    await page.getByRole('button',{name:'Open settings'}).click();
    await page.keyboard.press('Control+k');await palette.getByRole('textbox',{name:'Search destinations'}).fill('Chat');await palette.getByRole('button',{name:/^Chat/}).click();
    assert.equal(await message.inputValue(),'A draft that survives navigation');
    await page.locator('.chat-history').evaluate(node=>{node.scrollTop=0;});
    await capture(page,{path:path.join(output,`chat-${width}-${scale}.png`),fullPage:true});
    await page.getByRole('button',{name:'Use dark theme'}).click();await checkColors(page);
    await capture(page,{path:path.join(output,`chat-dark-${width}-${scale}.png`),fullPage:true});
    await page.getByRole('button',{name:'Use light theme'}).click();
    await page.evaluate(()=>{window.wayfinder.chat=async()=>({turns:[{id:'long',user_text:'Synthetic long reply',status:'running',assistant_text:Array(60).fill('A paragraph for scroll verification.').join('\n\n')}]});});
    await page.getByRole('button',{name:'Refresh conversation'}).click();
    const stop=page.getByRole('button',{name:'Stop generating'});await stop.waitFor();const stopBounds=await stop.boundingBox();assert(stopBounds&&stopBounds.y+stopBounds.height<=height,'Stop must stay in viewport');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollHeight<=innerHeight+1),true,'Long reply has no outer scroll');
    await page.locator('.chat-history').evaluate(node=>{node.scrollTop=0;});
    await page.getByRole('button',{name:'Refresh conversation'}).click();
    assert.equal(await page.locator('.chat-history').evaluate(node=>node.scrollTop),0,'Refresh preserves older reading position');
    await stop.click();
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
    await capture(page,{path:path.join(output,`agents-${width}-${scale}.png`),fullPage:true});
    await page.keyboard.press('Control+k');await palette.getByRole('textbox',{name:'Search destinations'}).fill('Runs');await palette.getByRole('button',{name:/^Runs & reviews/}).click();
    await page.getByRole('button',{name:'Select workflow document'}).click();await page.getByRole('button',{name:'Add step'}).click();
    await page.getByRole('button',{name:'Review and start workflow'}).click();
    await page.getByRole('heading',{name:/Selected-source workflow.*completed/}).waitFor();
    assert.equal(await page.getByRole('img',{name:'Workflow progress diagram'}).count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'Workflow has no horizontal overflow');
    await capture(page,{path:path.join(output,`workflow-${width}-${scale}.png`),fullPage:true});
    results.push({ width, height, scale, tier: 'rendered-synthetic-fixture', passed: true, checks: ['local fonts','semantic text contrast >=4.5:1','named icon controls','chat entry and explicit synthetic send','safe Markdown/code/table','remote model image blocked','theme','palette','scoped recall','long inert source','reading size applied','no overflow','setup state',...(width<=900?['drawer focus trap','Escape focus restoration','single modal','resize recovery']:[])] });
    await context.close();
  }
  for(const width of [1440,600]){
    const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
    await context.addInitScript(fixture,JSON.parse(await fs.readFile(path.join(root,'../wayfinder/platform/task-profiles.json'),'utf8')));
    const page=await context.newPage();page.on('pageerror',error=>faults.push(error.message));
    await page.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():(blocked.push(route.request().url()),route.abort()));
    await page.goto(origin+'?setup');
    await page.getByRole('heading',{name:'Start with a private foundation.'}).waitFor();
    assert.equal(await page.getByRole('button',{name:'Continue',exact:true}).isDisabled(),true);
    await capture(page,{path:path.join(output,`onboarding-local-${width}.png`),fullPage:true});
    await page.getByRole('button',{name:'Check / prepare database'}).click();
    await page.getByRole('button',{name:'Verify bundled memory model'}).click();
    await page.getByRole('button',{name:'Continue',exact:true}).click();
    await page.getByRole('button',{name:'Check Hermes connection'}).click();
    await page.getByText('Verified · valid for five minutes',{exact:true}).waitFor();
    await capture(page,{path:path.join(output,`onboarding-model-${width}.png`),fullPage:true});
    await page.getByRole('button',{name:'Continue',exact:true}).click();
    const finish=page.getByRole('button',{name:/Create workspace and open Wayfinder/});
    assert.equal(await finish.isDisabled(),true);
    await page.getByRole('checkbox',{name:/I agree to send/}).check();
    assert.equal(await finish.isEnabled(),true);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    await capture(page,{path:path.join(output,`onboarding-review-${width}.png`),fullPage:true});
    await finish.click();await page.getByRole('heading',{name:'A clearer plan',exact:true}).waitFor();
    results.push({width,tier:'rendered-synthetic-onboarding',passed:true,checks:['required checks','exact model consent','explicit finish','optional connections skipped','no horizontal overflow']});
    await context.close();
  }
  assert.deepEqual(blocked, [], 'Renderer attempted a nonlocal request');
  assert.deepEqual(faults, [], 'Renderer had uncaught errors');
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify({ results, blocked, faults, caveat: 'Synthetic renderer fixtures only. Does not qualify Electron IPC, live backend, providers or native actions.' }, null, 2));
  console.log(JSON.stringify({ passed: results.length, blocked, faults, report: path.join(output, 'report.json') }));
} finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
