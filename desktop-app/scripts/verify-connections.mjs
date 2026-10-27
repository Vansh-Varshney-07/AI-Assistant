/** Fresh packaged first-run check: app renderer only, no OS UI automation. */
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash,randomUUID} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const execute=promisify(execFile),require=createRequire(process.env.WAYFINDER_PLAYWRIGHT_MODULE||import.meta.url);
const {_electron:electron}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [profile,report,credentialSource]=process.argv.slice(2);assert(credentialSource&&path.isAbsolute(credentialSource));assert(profile&&report&&path.isAbsolute(profile));
await fs.mkdir(profile,{recursive:true});assert(!(await fs.readdir(profile)).length,'Fresh empty profile required');
const runtime=path.join(profile,'workspace-v1');
const id=createHash('sha256').update(path.resolve(runtime).toLowerCase()).digest('hex').slice(0,16);
const container='wayfinder-memory-'+id,volume='wayfinder-memory-data-'+id;
const env={...process.env,WAYFINDER_VERIFY_HIDDEN:'1',WAYFINDER_VERIFY_PROFILE:profile};
for(const key of ['WAYFINDER_PYTHON','WAYFINDER_PROJECT_ROOT','WAYFINDER_DESKTOP_RUNTIME','WAYFINDER_CHAT_PROVIDER_PIN','FALKORDB_HOST','FALKORDB_PORT','FALKORDB_PASSWORD','ELECTRON_RUN_AS_NODE'])delete env[key];
const checks=[];const check=(name,value)=>{assert(value,name);checks.push({name,passed:true});console.log('PASS',name);};
let application,context;
async function launch(){application=await electron.launch({executablePath:path.join(root,'release/win-unpacked/Wayfinder.exe'),env,timeout:150000});const page=await application.firstWindow();page.setDefaultTimeout(150000);return page;}
async function completed(page,space,cid,count){
  const deadline=Date.now()+150000;let data;
  do{data=await page.evaluate(({space,cid})=>window.wayfinder.chat(space,cid),{space,cid});if(data.turns.length>=count&&!['reserved','running'].includes(data.turns.at(-1).status))break;await new Promise(resolve=>setTimeout(resolve,700));}while(Date.now()<deadline);
  if(data.turns.at(-1)?.status!=='completed')console.log('TURN_DIAGNOSTIC',JSON.stringify(data));
  check('model_turn_completed_'+checks.length,data.turns.length>=count&&data.turns.at(-1).status==='completed');return data;
}
try{
  const imported=await execute(path.join(root,'release/win-unpacked/Wayfinder.exe'),['--import-connections-only',credentialSource],{env,windowsHide:true,timeout:30000});
  check('headless_import_confirms_three_connections',imported.stdout.includes('WAYFINDER_IMPORT=')&&['google','tavily','notion'].every(k=>imported.stdout.includes('"'+k+'":true')));
  const sealed=await fs.readFile(path.join(profile,'connections-v1.bin'));
  check('credentials_saved_as_ciphertext',sealed.length>100&&!sealed.includes(Buffer.from('refresh_token'))&&!sealed.includes(Buffer.from('https://oauth2.googleapis.com/token')));
  let page=await launch();await page.getByRole('heading',{name:'Make this your workspace.'}).waitFor();
  check('fresh_profile_shows_onboarding',true);
  check('window_stays_hidden',await application.evaluate(({BrowserWindow})=>BrowserWindow.getAllWindows().every(w=>!w.isVisible())));
  check('workspace_access_denied_before_setup',await page.evaluate(async()=>{try{await window.wayfinder.listSpaces();return false;}catch{return true;}}));
  check('finish_requires_checks_and_consent',await page.getByRole('button',{name:'Create workspace and open Wayfinder'}).isDisabled());
  await page.getByRole('button',{name:'Verify bundled memory model'}).click();await page.getByRole('button',{name:'✓ Memory model verified'}).waitFor();check('frozen_cpu_memory_inference',true);
  await page.getByRole('button',{name:'Check / prepare database'}).click();await page.getByRole('button',{name:'✓ Database ready'}).waitFor();check('isolated_private_database_prepared',true);
  await page.getByRole('button',{name:'Check Hermes connection'}).click();await page.getByRole('button',{name:'✓ Model connection verified'}).waitFor();check('installed_hermes_isolation_verified',true);
  await page.getByLabel('Workspace name',{exact:true}).fill('New user acceptance');await page.getByLabel(/I agree to send/).check();await page.getByRole('button',{name:'Create workspace and open Wayfinder'}).click();
  await page.getByText('Backend connected',{exact:true}).waitFor();
  let state=await page.evaluate(()=>window.wayfinder.status());check('real_owned_backend_chat_ready',state.state==='ready'&&state.capabilities.general_chat&&state.release.variant==='workspace-parity');
  await page.waitForFunction(()=>document.querySelector('[aria-label="Memory space"]').value);
  const sid=await page.getByLabel('Memory space').inputValue();check('first_space_created',!!sid);
  const config=JSON.parse(await fs.readFile(path.join(profile,'onboarding.json'),'utf8'));context=config.context;
  check('setup_stores_no_provider_secrets',Object.keys(config.model).sort().join(',')==='endpoint,model,provider'&&!JSON.stringify(config).includes('password'));
  const connectionState=await page.evaluate(s=>window.wayfinder.connectionsStatus(s),sid);
  check('three_connections_reach_frozen_backend',Object.values(connectionState.configured).every(Boolean)&&Object.keys(connectionState.checks).length===0);
  await page.getByRole('button',{name:'Connections',exact:true}).first().click();
  for(const [provider,label] of [['google','Google'],['notion','Notion'],['tavily','Tavily']]){
    await page.getByRole('button',{name:'Check '+label+' connection',exact:true}).click();
    await page.waitForFunction(({sid,provider})=>window.wayfinder.connectionsStatus(sid).then(s=>s.checks[provider]?.passed),{sid,provider});
    check('packaged_'+provider+'_live_check',true);
  }
  for(const service of ['calendar','tasks','gmail_headers','drive','contacts']){
    console.log('STEP google_source',service);
    await page.getByLabel('Google source',{exact:true}).selectOption(service,{timeout:10000});
    console.log('STEP google_read_click',service);
    await page.getByRole('button',{name:'Read selected Google source',exact:true}).click();
    console.log('STEP google_read_wait',service);
    await page.getByRole('region',{name:'Connection results',exact:true}).waitFor({timeout:30000});
    await page.waitForFunction(()=>!document.querySelector('[role="status"]')?.textContent?.includes('Running a bounded'));
    check('packaged_google_'+service+'_renders_read_results',await page.getByRole('region',{name:'Connection results',exact:true}).isVisible());
  }
  await page.getByLabel('Web search query',{exact:true}).fill('Python official documentation');
  await page.getByRole('button',{name:'Search web',exact:true}).click();
  await page.waitForFunction(()=>!document.querySelector('[role="status"]')?.textContent?.includes('Running a bounded'));
  check('tavily_search_renders_bounded_sources',await page.locator('.connection-results .connection-record').count()>0&&await page.locator('.connection-results .connection-record').count()<=3);
  await page.getByRole('button',{name:'Search Notion',exact:true}).click();
  await page.getByRole('button',{name:'Read this Notion page',exact:true}).first().waitFor();
  await page.getByRole('button',{name:'Read this Notion page',exact:true}).first().click();
  await page.waitForFunction(()=>!document.querySelector('[role="status"]')?.textContent?.includes('Running a bounded'));
  check('notion_explicit_page_read_renders_excerpt',await page.locator('.connection-results .connection-record').count()===1);
  const notShared=await page.evaluate(s=>window.wayfinder.inventory(s),sid);
  check('account_reads_not_automatically_saved_as_memory',notShared.records.length===0);
  await page.getByRole('button',{name:'Chat',exact:true}).first().click();await page.getByRole('button',{name:'New conversation',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('[aria-label="Conversation"]').value);
  const cid=await page.getByLabel('Conversation',{exact:true}).inputValue();const nonce='wayfinder-'+randomUUID().slice(0,8);
  await page.getByLabel('Message',{exact:true}).fill('For this conversation, the synthetic test code is '+nonce+'. Reply with just that code.');await page.getByRole('button',{name:'Send message',exact:true}).click();
  const first=await completed(page,sid,cid,1);check('actual_model_reply_contains_new_nonce',first.turns.at(-1).assistant_text.includes(nonce));
  await page.getByLabel('Message',{exact:true}).fill('What is the synthetic test code I gave you in the previous message? Reply with just that code.');await page.getByRole('button',{name:'Send message',exact:true}).click();
  const second=await completed(page,sid,cid,2);check('actual_model_uses_canonical_history',second.turns.at(-1).assistant_text.includes(nonce)&&second.turns.at(-1).history_count===2);
  const inventory=await page.evaluate(s=>window.wayfinder.inventory(s),sid);check('chat_does_not_publish_automatic_memory',inventory.records.length===0);

  const generation=state.instance_generation;await application.close();application=undefined;
  page=await launch();await page.getByText('Backend connected',{exact:true}).waitFor();state=await page.evaluate(()=>window.wayfinder.status());
  check('restart_creates_fresh_backend',state.instance_generation!==generation&&state.capabilities.general_chat);
  const restored=await page.evaluate(s=>window.wayfinder.connectionsStatus(s),sid);
  check('encrypted_credentials_survive_restart',Object.values(restored.configured).every(Boolean)&&Object.keys(restored.checks).length===0);
  const grant=await page.evaluate(s=>window.wayfinder.externalGrant(s,{provider:'notion',intent:'search',query:''}),sid);
  await page.evaluate(()=>window.wayfinder.disconnectConnection('notion'));
  check('local_disconnect_invalidates_existing_grant',await page.evaluate(async({sid,grant})=>{try{await window.wayfinder.externalRead(sid,grant);return false;}catch{return true;}},{sid,grant:grant.id}));
  check('local_disconnect_reaches_backend',!(await page.evaluate(s=>window.wayfinder.connectionsStatus(s),sid)).configured.notion);
  const persisted=await page.evaluate(({sid,cid})=>window.wayfinder.chat(sid,cid),{sid,cid});check('restart_preserves_real_conversation_without_replay',persisted.turns.length===2&&persisted.turns.every(t=>t.status==='completed'));
  check('app_needs_no_development_checkout_or_python_env',!env.WAYFINDER_PROJECT_ROOT&&!env.WAYFINDER_PYTHON&&await fs.stat(path.join(root,'release/win-unpacked/resources/backend/WayfinderBackend.exe')).then(s=>s.isFile()));
  await application.close();application=undefined;
  const evidence={tier:'actual hidden packaged Windows app + bundled Python/CPU model + private persistent Docker database + installed managed Hermes provider',checks,passed:checks.length,native_desktop_automation:false,google_connected:true,tavily_connected:true,notion_connected:true,credential_storage: "Windows safeStorage",provider_writes:false,prerequisites:['Docker Desktop local Linux engine','Existing managed Hermes/OpenShell with configured provider'],profile,asar_sha256:createHash('sha256').update(await fs.readFile(path.join(root,'release/win-unpacked/resources/app.asar'))).digest('hex')};
  await fs.writeFile(report,JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence));
}catch(error){if(application){const page=await application.firstWindow().catch(()=>null);if(page)console.log('APP_ERRORS',JSON.stringify(await page.getByRole('alert').allTextContents()));}throw new Error('Packaged connection qualification failed after '+checks.length+' checks: '+String(error?.name||'Error'));}
finally{
  if(application)await application.close();
  await fs.rm(path.join(profile,'connections-v1.bin'),{force:true});
  // Cleanup names are derived from this newly created isolated profile only.
  context=context||'desktop-linux';
  for(const [kind,name,args] of [['container',container,['rm','-f',container]],['volume',volume,['volume','rm',volume]]]){
    try{const {stdout}=await execute('docker',['--context',context,kind,'inspect',name],{windowsHide:true});const item=JSON.parse(stdout)[0],labels=kind==='container'?item.Config.Labels:item.Labels;if(labels?.['wayfinder.app']==='local.wayfinder.desktop'&&labels?.['wayfinder.workspace']===id)await execute('docker',['--context',context,...args],{windowsHide:true});}catch{}
  }
}
