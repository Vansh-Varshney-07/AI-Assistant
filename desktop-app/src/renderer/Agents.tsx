import React,{useEffect,useState} from 'react';
import {FileText,Layers3,ShieldCheck,ArrowUpRight,Square} from 'lucide-react';
import type {DesktopAPI,Row} from '../shared/types';
import type {WorkspacePage} from './Workspace';
interface Props{space:string;api:DesktopAPI;busy:boolean;act:(job:()=>Promise<any>,then?:(value:any)=>void)=>Promise<void>;files:Row|null;setFiles:(value:Row|null)=>void;go:(page:WorkspacePage)=>void}
export function AgentsPanel({space,api,busy,act,files,setFiles,go}:Props){
  const [catalog,setCatalog]=useState<Row|null>(null),[error,setError]=useState('');
  const [profile,setProfile]=useState('A05'),[goal,setGoal]=useState('Create a study guide from this document, with key ideas, examples and questions. Cite the supplied source and state any gaps.');
  const [run,setRun]=useState<Row|null>(null),[history,setHistory]=useState<Row[]>([]);
  useEffect(()=>{let alive=true;setCatalog(null);setRun(null);setHistory([]);setError('');setProfile('A05');
    setGoal('Create a study guide from this document, with key ideas, examples and questions. Cite the supplied source and state any gaps.');
    void Promise.all([api.profiles(space),api.profileTasks(space)]).then(([c,h])=>{if(alive){setCatalog(c);setHistory(h);}}).catch(e=>{if(alive)setError(e.message);});return()=>{alive=false;};},[space,api]);
  useEffect(()=>{if(!run || !['reserved','running'].includes(run.status))return;let alive=true,polling=false;
    const timer=setInterval(()=>{if(polling)return;polling=true;void api.profileTask(space,run.id).then(value=>{if(alive)setRun(value);}).catch(e=>{if(alive)setError(e.message);}).finally(()=>{polling=false;});},1500);
    return()=>{alive=false;clearInterval(timer);};},[run?.id,run?.status,space,api]);
  const chosen=catalog?.profiles?.find((p:Row)=>p.id===profile),file=files?.files?.[0];
  const start=()=>void act(()=>api.startProfileTask(space,profile,file.id,goal),setRun);
  return <div className="agents-page"><section className="policy-summary"><Layers3 size={27}/><div><h2>One assistant. Profiles for complete tasks.</h2><p>M00 routes the task to one lead. Profiles and app presets share existing workers and trusted services; they do not start a permanent agent fleet.</p><p className="hint">Current execution: one selected-file task through W35, tools closed, no helpers. General conversation and account-backed workflows remain unqualified.</p></div></section>
    {error&&<p role="alert" className="message error">{error}</p>}
    {!catalog?<p role="status">Loading actual profile availability…</p>:<>
    <div className="section-heading"><div><h3>Task profiles</h3><span>Version {catalog.version} · availability is per operation</span></div><button onClick={()=>go('capabilities')}>Inspect Hermes runtime</button></div>
    <div className="profile-grid">{catalog.profiles.map((p:Row)=><button className={`profile-card ${profile===p.id?'selected':''}`} key={p.id} aria-label={`Select ${p.id} ${p.name}`} aria-pressed={profile===p.id} onClick={()=>{if(p.id==='A07')go('memory');else setProfile(p.id);}}><span className="section-code">{p.id}</span><strong>{p.name}</strong><span className="badge">{p.execution.status.replaceAll('_',' ')}</span><small>{p.execution.note}</small>{p.id==='A07'&&<span>Open existing Memory view <ArrowUpRight size={13}/></span>}</button>)}</div>
    <section className="panel-form"><h3>Run a selected-file task · {chosen?.name}</h3><p className="hint">A01 researches supplied sources only. A05 builds explanations and study guides. A06 analyzes authorized files. The same scoped W35 handler serves each; no tool or account access is added by switching profiles.</p>
      {!chosen?.execution.included?<p className="inline-note">{chosen?.execution.note} This profile has no execution fallback.</p>:<>
      {!chosen.execution.available&&<p className="inline-note">Inspect the installed Hermes runtime in Capabilities before analysis. A registered profile is not qualification.</p>}
      <button disabled={busy} onClick={()=>void act(()=>api.selectFiles(space,'document'),value=>{if(value)setFiles(value);})}><FileText size={16}/>Select task document</button>
      {file&&<p>Selected: <strong>{file.name}</strong> · {file.bytes} bytes</p>}
      <label>Task goal<textarea aria-label="Task goal" value={goal} maxLength={1000} onChange={e=>setGoal(e.target.value)} rows={4}/></label>
      <div className="form-footer"><span>One existing W35 run · trusted disclosure before dispatch</span><button className="primary" disabled={busy||!file||!goal.trim()||!chosen.execution.available} onClick={start}>Run selected-file task <ArrowUpRight size={14}/></button></div>
      </>}
    </section>
    {run&&<section className="workspace-panel" aria-label="Task outcome"><div className="section-heading"><div><h3>{run.profile_id} task result</h3><span>{run.goal}</span></div><span className="badge">{run.status}</span></div>
      {run.warning&&<p className="inline-note">{run.warning}</p>}
      {run.result?<><pre className="answer-text">{run.result.text}</pre><h4>Supplied source evidence</h4>{run.result.sources.map((source:Row)=><div className="observation" key={source.reference}><strong>{source.name}</strong><p><code>{source.sha256}</code></p><p>{source.truncated?'Partial extraction: source text exceeded the existing worker limit.':'Source identity/hash checked when the task completed.'}</p></div>)}<p className="footnote">Historical model artifact. Source verification does not establish factual accuracy. Tokens and model cost are unknown.</p></>:<p className="muted">{['running','reserved'].includes(run.status)?'Generating from the selected source. No simulated streaming.':'No completed artifact is asserted.'}</p>}
      <div className="inline-actions">{['running','reserved'].includes(run.status)?<button disabled={busy} onClick={()=>void act(()=>api.cancelProfileTask(space,run.id),setRun)}><Square size={13}/>Stop task</button>:<button disabled={busy} onClick={()=>void act(()=>api.clearProfileTask(space,run.id),()=>{setRun(null);void api.profileTasks(space).then(setHistory);})}>Clear this task artifact</button>}<span className="hint">{run.metrics.worker_invocations} worker invocation · {run.metrics.delegations} delegations</span></div>
    </section>}
    <div className="section-heading"><div><h3>App presets</h3><span>Shared profile focus; account permissions stay separate</span></div></div>
    <div className="connection-grid">{catalog.presets.map((p:Row)=><section className="connection-card" key={p.id}><span className="section-code">{p.id}</span><h3>{p.name}</h3><p>Lead {p.lead}{p.helpers.length?` · eligible helpers ${p.helpers.join(', ')}`:''}</p><span className="badge">Provider operations unqualified</span><p className="hint">Requires {p.required_connections.join(', ')}. No account, read or write access is inferred.</p></section>)}</div>
    <div className="section-heading"><div><h3>Recent task records</h3><span>Eight most recent; opening observes without replay</span></div><button disabled={busy} onClick={()=>void act(()=>api.profileTasks(space),setHistory)}>Refresh task records</button></div>
    {history.length?history.map(row=><button className="activity-row" key={row.id} onClick={()=>void act(()=>api.profileTask(space,row.id),setRun)}><ShieldCheck size={16}/><div><strong>{row.profile_id} · {row.goal}</strong><small>{row.status}</small></div></button>):<p className="empty-inline">No prior profile tasks in this scope.</p>}
    </>}
  </div>;
}
