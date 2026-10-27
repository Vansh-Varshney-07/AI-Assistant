import React,{useEffect,useRef,useState} from 'react';
import {ArrowUp,CheckCircle2,Compass,MessageSquare,Plus,RefreshCw,ShieldCheck,Square,Trash2} from 'lucide-react';
import type {DesktopAPI,Row} from '../shared/types';
import {Markdown} from './Markdown';

const generating=(data:Row)=>data.turns?.some((turn:Row)=>['reserved','running'].includes(turn.status));
const message=(error:unknown)=>error instanceof Error?error.message:'The operation was not confirmed.';

export function ChatPanel({api,space,qualified}:{api:DesktopAPI;space:string;qualified:boolean}){
  const [list,setList]=useState<Row[]>([]),[id,setId]=useState(''),[data,setData]=useState<Row>({turns:[]});
  const [draft,setDraft]=useState(''),[busy,setBusy]=useState(false),[listLoading,setListLoading]=useState(true),[conversationLoading,setConversationLoading]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[deleting,setDeleting]=useState(false);
  const epoch=useRef(0),selection=useRef(''),lock=useRef(false),active=useRef(false),history=useRef<HTMLDivElement>(null),follow=useRef(true),composing=useRef(false),revision=useRef(0);
  const loading=listLoading||conversationLoading;
  const pendingKey='wayfinder-pending-chat:'+space;
  active.current=!!generating(data);
  function choose(value:string){revision.current++;setConversationLoading(!!value);selection.current=value;setId(value);setDraft('');setData({turns:[]});setDeleting(false);setError('');setNotice('');follow.current=true;}
  useEffect(()=>{
    const current=++epoch.current;lock.current=false;setBusy(false);choose('');setList([]);setListLoading(true);
    void api.chats(space).then(rows=>{if(current===epoch.current){setList(rows);choose(rows[0]?.id||'');}}).catch(e=>{if(current===epoch.current)setError(message(e));}).finally(()=>{if(current===epoch.current)setListLoading(false);});
    return()=>{epoch.current++;};
  },[api,space]);
  useEffect(()=>{
    if(!id)return;let alive=true,polling=false;setConversationLoading(true);
    async function refresh(){if(polling)return;polling=true;const version=revision.current;const valid=()=>alive&&selection.current===id&&version===revision.current;try{const result=await api.chat(space,id);if(valid())setData(result);}catch(e){if(valid())setError(message(e));}finally{polling=false;if(valid())setConversationLoading(false);}}
    void refresh();const timer=setInterval(()=>{if(active.current)void refresh();},1800);
    return()=>{alive=false;clearInterval(timer);};
  },[api,space,id]);
  useEffect(()=>{const node=history.current;if(node&&follow.current)node.scrollTop=node.scrollHeight;},[data]);
  async function perform(job:(isCurrent:()=>boolean)=>Promise<void>){
    if(lock.current)return;const current=epoch.current,cid=selection.current;
    const isCurrent=()=>current===epoch.current&&cid===selection.current;
    lock.current=true;setBusy(true);setError('');setNotice('');
    try{await job(isCurrent);}catch(e){if(isCurrent())setError(message(e));}finally{if(current===epoch.current){lock.current=false;setBusy(false);}}
  }
  function create(){void perform(async valid=>{const row=await api.newChat(space);if(valid()){setList(old=>[row,...old]);choose(row.id);}});}
  function send(){
    if(loading||!id||!draft.trim()||generating(data))return;
    const text=draft,cid=id;
    void perform(async valid=>{
      // Only an opaque request ID persists. It is an observation hint, never a
      // prompt/replay queue. A lost acknowledgement needs observation first.
      const pending=localStorage.getItem(pendingKey);
      if(pending){
        let previous:Row;
        try{previous=JSON.parse(pending);if(typeof previous.conversation!=='string'||typeof previous.request!=='string')throw new Error();}
        catch{localStorage.removeItem(pendingKey);throw new Error('The previous send hint was invalid. Nothing was sent. Review the conversation and send explicitly again.');}
        const known=await api.lookupChat(space,previous.conversation,previous.request);
        if(!valid())return;
        localStorage.removeItem(pendingKey);
        if(known.accepted){if(previous.conversation===cid){const observed=await api.chat(space,cid);if(!valid())return;setData(observed);}else choose(previous.conversation);setNotice('The previous send was accepted. Its conversation has been reopened; no new message was sent.');}
        else setNotice('The previous send was not acknowledged. No request was replayed. Review the conversation, then explicitly send a new message.');
        return;
      }
      revision.current++;
      const request=crypto.randomUUID();localStorage.setItem(pendingKey,JSON.stringify({conversation:cid,request}));
      let result:Row;
      try{result=await api.sendChat(space,cid,request,text);localStorage.removeItem(pendingKey);}
      catch(e){throw new Error(message(e)+' No automatic retry was made. Refresh to observe the conversation before sending again.');}
      if(!valid())return;
      follow.current=true;setData(result);setDraft('');
      const rows=await api.chats(space);if(valid())setList(rows);
    });
  }
  function stop(){const turn=data.turns?.find((t:Row)=>['reserved','running'].includes(t.status));if(!turn)return;void perform(async valid=>{revision.current++;const result=await api.cancelChat(space,id,turn.id);if(valid())setData(result);});}
  function refresh(){void perform(async valid=>{revision.current++;const [rows,result]=await Promise.all([api.chats(space),id?api.chat(space,id):Promise.resolve({turns:[]})]);if(valid()){setList(rows);setData(result);setNotice('Conversation state refreshed. Nothing was replayed.');}});}
  function remove(){void perform(async valid=>{revision.current++;await api.deleteChat(space,id);const rows=await api.chats(space);if(valid()){setList(rows);choose(rows[0]?.id||'');}});}
  function earlier(){void perform(async valid=>{revision.current++;const old=await api.chat(space,id,data.before);if(valid()){follow.current=false;setData(current=>({...current,turns:[...old.turns,...current.turns],before:old.before,has_more:old.has_more}));}});}
  return <div className="chat-panel">
    <div className="chat-toolbar"><div className="chat-identity"><span className="identity-icon"><Compass size={22}/></span><div><strong>Wayfinder</strong><span>Your conversation, in this space</span></div></div><div className="chat-controls"><button disabled={busy} onClick={refresh} aria-label="Refresh conversation"><RefreshCw size={16}/></button><button className="primary" disabled={busy||generating(data)} onClick={create}><Plus size={16}/>New conversation</button></div></div>
    <div className="chat-selection"><label className="sr-only" htmlFor="conversation">Conversation</label><select id="conversation" value={id} disabled={busy||loading} onChange={e=>choose(e.target.value)}><option value="">Choose a conversation</option>{list.map(row=><option key={row.id} value={row.id}>{row.title}</option>)}</select><button className="icon-button" aria-label="Delete conversation" disabled={busy||!id||loading||generating(data)} onClick={()=>setDeleting(true)}><Trash2 size={16}/></button></div>
    {deleting&&<section className="delete-review" aria-label="Delete conversation review"><strong>Delete this local conversation?</strong><p>This removes its chat and worker artifacts. Memory, backups and provider records remain.</p><div className="inline-actions"><button disabled={busy} onClick={()=>setDeleting(false)}>Keep conversation</button><button className="danger" disabled={busy} onClick={remove}>Delete this conversation</button></div></section>}
    {error&&<p className="message error" role="alert">{error}</p>}{notice&&<p className="message" role="status">{notice}</p>}
    {!qualified&&<p className="inline-note">Your approved model connection will be rechecked before sending. If it has changed, Wayfinder asks you to verify it in setup.</p>}
    <div className="chat-history" ref={history} role="log" aria-label="Conversation messages" aria-live="polite" aria-busy={loading} onScroll={()=>{const node=history.current;if(node)follow.current=node.scrollHeight-node.scrollTop-node.clientHeight<80;}}>
      {loading?<p className="chat-loading" role="status">Loading your conversation…</p>:!data.turns?.length?<div className="chat-welcome"><span className="welcome-orbit"><MessageSquare size={32}/></span><h2>What would you like to untangle?</h2><p>Think through an idea, get an explanation or start a draft.</p>{!id?<button onClick={create} disabled={busy}><Plus size={16}/>Start a conversation</button>:<div className="chat-starters">{['Help me think through a decision','Explain a concept step by step','Help me draft something clear'].map(prompt=><button key={prompt} onClick={()=>setDraft(prompt)}>{prompt}</button>)}</div>}<span className="chat-boundary"><ShieldCheck size={14}/>Chat has no tools. Memory changes use a separate review.</span></div>:<>
        {data.has_more&&<button className="load-earlier" disabled={busy||generating(data)} onClick={earlier}>Load earlier messages</button>}
        {data.turns.map((turn:Row)=><article className="chat-turn" key={turn.id}><div className="chat-user"><strong>You</strong><p>{turn.user_text}</p></div><div className="chat-assistant"><strong><Compass size={15}/>Wayfinder</strong>{turn.assistant_text?<Markdown text={turn.assistant_text}/>:<p className="generation-state">{['reserved','running'].includes(turn.status)?<><span className="activity-pulse"/>{turn.status==='reserved'?'Request accepted · waiting for worker':'Generating a reply…'}</>:turn.warning||turn.status}</p>}<small className={`turn-status ${turn.status}`}>{turn.status==='completed'&&<CheckCircle2 size={12}/>} {turn.status}{turn.warning&&turn.assistant_text?' · '+turn.warning:''}</small></div></article>)}
      </>}
    </div>
    <form className="chat-compose" onSubmit={e=>{e.preventDefault();send();}}><label className="sr-only" htmlFor="chat-message">Message</label><textarea id="chat-message" rows={3} maxLength={4000} value={draft} disabled={busy||loading||!id||generating(data)} onChange={e=>setDraft(e.target.value)} onCompositionStart={()=>{composing.current=true;}} onCompositionEnd={()=>{composing.current=false;}} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing&&!composing.current&&e.keyCode!==229){e.preventDefault();send();}}} placeholder={!id?'Start a conversation above…':'Ask, explore, or work through an idea…'}/><div className="composer-actions"><span>Enter to send · Shift+Enter for a new line</span>{generating(data)?<button type="button" disabled={busy} onClick={stop}><Square size={14}/>Stop generating</button>:<button className="primary send-message" aria-label="Send message" disabled={busy||loading||!id||!draft.trim()}><ArrowUp size={18}/></button>}</div></form>
    <p className="chat-footnote">Replies can be wrong. Up to six completed message pairs are sent to your approved model. Stopping locally does not confirm provider abort or billing.</p>
  </div>;
}
