/** Hidden actual Windows application test. No OS driver, desktop capture or native dialogs. */
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const require=createRequire(process.env.WAYFINDER_PLAYWRIGHT_MODULE || import.meta.url);
const { _electron:electron }=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const project=path.dirname(root);
const [runtime, report]=process.argv.slice(2);
assert(runtime && report && path.isAbsolute(runtime),'Explicit disposable runtime and report required');
const profile=path.join(path.dirname(runtime),'verification-profile');
await fs.mkdir(profile,{recursive:true});
const env={ ...process.env, WAYFINDER_VERIFY_HIDDEN:'1',WAYFINDER_VERIFY_PROFILE:profile,WAYFINDER_PROJECT_ROOT:project,WAYFINDER_DESKTOP_RUNTIME:runtime };
delete env.ELECTRON_RUN_AS_NODE;
let application;
const checks=[];
const check=(name,value)=>{ assert(value,name);checks.push({name,passed:true}); };
async function launch(){
  application=await electron.launch({executablePath:path.join(root,'release/win-unpacked/Wayfinder.exe'),env,timeout:120000});
  const page=await application.firstWindow();
  page.setDefaultTimeout(120000);
  await page.getByText('Backend connected',{exact:true}).waitFor();
  check('window_never_shown',await application.evaluate(({BrowserWindow})=>BrowserWindow.getAllWindows().every(w=>!w.isVisible())));
  const state=await page.evaluate(()=>window.wayfinder.status());
  check('owned_manifest_pairing',state.state==='ready'&&state.release?.variant==='workspace-parity'&&typeof state.instance_generation==='string');
  return {page,state};
}
try{
  let {page,state}=await launch();
  const generation=state.instance_generation;
  await page.getByRole('button',{name:'Create a space',exact:true}).first().click();
  await page.getByLabel('Space name').fill('Synthetic packaged application test');
  await page.getByRole('button',{name:'Create space',exact:true}).click();
  await page.getByRole('heading',{name:'Good day, Operator.'}).waitFor();
  const sid=await page.getByLabel('Memory space').inputValue();
  check('actual_space_created',!!sid);
  const profiles=await page.evaluate(s=>window.wayfinder.profiles(s),sid);
  check('actual_profile_inventory_and_unqualified_presets',profiles.main.id==='M00'&&profiles.profiles.length===8&&profiles.presets.length===6&&profiles.presets.every(p=>!p.available));
  await page.getByRole('button',{name:'Agents & apps',exact:true}).first().click();
  await page.getByRole('heading',{name:'Task profiles',exact:true}).waitFor();
  check('actual_agents_screen_requires_selection_and_qualification',await page.getByRole('button',{name:'Run selected-file task'}).isDisabled());
  await page.getByRole('button',{name:'Memory',exact:true}).first().click();
  await page.getByLabel('Memory field').fill('retention_days');
  await page.getByRole('button',{name:'Recall memory',exact:true}).click();
  await page.getByText('missing',{exact:true}).first().waitFor();
  check('actual_empty_memory_not_sample_data',true);
  await page.getByRole('button',{name:'Propose memory',exact:true}).click();
  const form=page.locator('form').filter({has:page.getByRole('heading',{name:'Propose a fact',exact:true})});
  await form.getByLabel('Field',{exact:true}).fill('retention_days');
  await form.getByLabel('Value',{exact:false}).fill('30');
  await form.getByLabel('Your source statement').fill('Synthetic proposed retention is 30 days; not approved.');
  await form.getByRole('button',{name:'Create review',exact:true}).click();
  await page.getByRole('heading',{name:'Pending memory review',exact:true}).waitFor();
  const before=await page.evaluate(s=>window.wayfinder.recall(s,'me','retention_days','now'),sid);
  check('proposal_has_no_memory_effect',before.packet.answer_status==='missing');
  const snapshot=await page.evaluate(s=>window.wayfinder.snapshot(s),sid);
  check('proposal_persisted_pending',snapshot.actions.length===1&&snapshot.actions[0].status==='pending');
  await page.getByRole('button',{name:'Reject',exact:true}).click();
  await page.waitForFunction(s=>window.wayfinder.snapshot(s).then(v=>v.actions[0]?.status==='rejected'),sid);
  check('real_rejection_no_native_confirmation',true);
  const denied=await page.evaluate(async s=>{
    const results=[];
    for(const operation of [()=>window.wayfinder.inventory('foreign-space'),()=>window.wayfinder.analyze(s,'unselected','Do not dispatch')]){
      try{await operation();results.push(false);}catch{results.push(true);}
    }
    return results;
  },sid);
  check('foreign_scope_and_unselected_model_input_denied',denied.every(Boolean));
  check('no_generic_renderer_escape',await page.evaluate(()=>!('invoke'in window.wayfinder)&&!('exec'in window.wayfinder)&&typeof window.require==='undefined'));
  await page.screenshot({path:path.join(root,'test-results/packaged-memory.png'),fullPage:true});
  await application.close();application=undefined;
  ({page,state}=await launch());
  check('restart_has_fresh_instance_generation',state.instance_generation!==generation);
  const after=await page.evaluate(s=>window.wayfinder.snapshot(s),sid);
  const recall=await page.evaluate(s=>window.wayfinder.recall(s,'me','retention_days','now'),sid);
  check('restart_preserves_rejected_receipt_without_replay',after.actions.length===1&&after.actions[0].status==='rejected'&&recall.packet.answer_status==='missing');
  check('restart_keeps_owned_runtime_identity',state.runtime===runtime);
  await application.close();application=undefined;
  const asar_sha256=createHash('sha256').update(await fs.readFile(path.join(root,'release/win-unpacked/resources/app.asar'))).digest('hex');
  const evidence={tier:'actual hidden packaged Windows Electron + real preload/main/Python/API + disposable actual neural storage',asar_sha256,checks,passed:checks.length,native_desktop_automation:false,native_dialogs_exercised:false,live_google:false,model_chat:false};
  await fs.writeFile(report,JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify(evidence));
}finally{if(application)await application.close();}
