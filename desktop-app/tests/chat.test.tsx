import React from 'react';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {ChatPanel} from '../src/renderer/Chat';

beforeEach(()=>localStorage.clear());
afterEach(()=>vi.useRealTimers());
const completed={turns:[{id:'turn',status:'completed',user_text:'Synthetic question',assistant_text:'## Synthetic answer\n\nA useful reply.'}]};
function client(){return {chats:vi.fn(async(space:string)=>[{id:space,title:'Synthetic conversation'}]),chat:vi.fn(async()=>({turns:[]})),sendChat:vi.fn(async()=>completed),newChat:vi.fn(async()=>({id:'new',title:'New conversation'})),cancelChat:vi.fn(async()=>({turns:[]})),lookupChat:vi.fn(async()=>({accepted:true})),deleteChat:vi.fn(async()=>({deleted:true}))} as any;}
async function ready(api:any,space='a'){const view=render(<ChatPanel api={api} space={space} qualified/>);await waitFor(()=>expect((screen.getByRole('textbox',{name:'Message'}) as HTMLTextAreaElement).disabled).toBe(false));return view;}

it('sends once on Enter and preserves Shift+Enter and IME composition',async()=>{
  const api=client();await ready(api);const input=screen.getByRole('textbox',{name:'Message'});
  fireEvent.change(input,{target:{value:'Synthetic question'}});
  fireEvent.keyDown(input,{key:'Enter',shiftKey:true});fireEvent.compositionStart(input);fireEvent.keyDown(input,{key:'Enter'});
  expect(api.sendChat).not.toHaveBeenCalled();fireEvent.compositionEnd(input);
  fireEvent.keyDown(input,{key:'Enter'});fireEvent.keyDown(input,{key:'Enter'});
  await screen.findByRole('heading',{name:'Synthetic answer'});
  expect(api.sendChat).toHaveBeenCalledTimes(1);expect(api.sendChat.mock.calls[0]).toEqual(['a','a',expect.any(String),'Synthetic question']);
});

it('does not display a late response or error in another space',async()=>{
  const api=client();let finish!:(value:any)=>void;api.sendChat.mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
  const view=await ready(api);fireEvent.change(screen.getByRole('textbox',{name:'Message'}),{target:{value:'PRIVATE_A'}});fireEvent.click(screen.getByRole('button',{name:'Send message'}));
  await waitFor(()=>expect(api.sendChat).toHaveBeenCalledTimes(1));
  await act(async()=>{view.rerender(<ChatPanel api={api} space="b" qualified/>);});
  await act(async()=>{finish({turns:[{id:'old',user_text:'PRIVATE_A',assistant_text:'PRIVATE_A_REPLY',status:'completed'}]});});
  expect(screen.queryByText('PRIVATE_A_REPLY')).toBeNull();expect((screen.getByRole('textbox',{name:'Message'}) as HTMLTextAreaElement).value).toBe('');
});

it('observes an uncertain send before allowing another explicit request',async()=>{
  const api=client();api.sendChat.mockRejectedValueOnce(new Error('Acknowledgement lost'));const view=await ready(api);
  fireEvent.change(screen.getByRole('textbox',{name:'Message'}),{target:{value:'PROMPT_NOT_STORED'}});fireEvent.click(screen.getByRole('button',{name:'Send message'}));
  await screen.findByRole('alert');const hint=localStorage.getItem('wayfinder-pending-chat:a')!;
  expect(hint).not.toContain('PROMPT_NOT_STORED');expect(JSON.parse(hint).request).toBeTruthy();
  api.chat.mockResolvedValue(completed);fireEvent.click(screen.getByRole('button',{name:'Send message'}));
  await screen.findByText(/previous send was accepted/);expect(api.lookupChat).toHaveBeenCalledTimes(1);expect(api.sendChat).toHaveBeenCalledTimes(1);
  expect(screen.getByRole('heading',{name:'Synthetic answer'})).toBeTruthy();view.unmount();
});

it('stops the known turn and requires a review before deletion',async()=>{
  const api=client();api.chat.mockResolvedValue({turns:[{id:'running',status:'running',user_text:'Question'}]});
  render(<ChatPanel api={api} space="a" qualified/>);await screen.findByText('Generating a reply…');
  fireEvent.click(screen.getByRole('button',{name:'Stop generating'}));await waitFor(()=>expect(api.cancelChat).toHaveBeenCalledWith('a','a','running'));
  await waitFor(()=>expect((screen.getByRole('button',{name:'Delete conversation'}) as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByRole('button',{name:'Delete conversation'}));expect(api.deleteChat).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Keep conversation'}));expect(screen.queryByLabelText('Delete conversation review')).toBeNull();
});

it('keeps the composer disabled until the selected conversation history arrives',async()=>{
  const api=client();let finish!:(value:any)=>void;api.chat.mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
  render(<ChatPanel api={api} space="a" qualified/>);
  await waitFor(()=>expect(api.chat).toHaveBeenCalledWith('a','a'));
  expect((screen.getByRole('textbox',{name:'Message'}) as HTMLTextAreaElement).disabled).toBe(true);
  await act(async()=>{finish({turns:[]});});
  expect((screen.getByRole('textbox',{name:'Message'}) as HTMLTextAreaElement).disabled).toBe(false);
});

it('does not let an older poll undo a confirmed local cancellation',async()=>{
  vi.useFakeTimers();const api=client();let finish!:(value:any)=>void;
  const running={turns:[{id:'running',status:'running',user_text:'Question'}]};
  api.chat.mockResolvedValueOnce(running).mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
  await act(async()=>{render(<ChatPanel api={api} space="a" qualified/>);});
  await act(async()=>{vi.advanceTimersByTime(1801);});expect(api.chat).toHaveBeenCalledTimes(2);
  await act(async()=>{fireEvent.click(screen.getByRole('button',{name:'Stop generating'}));});
  expect(screen.queryByRole('button',{name:'Stop generating'})).toBeNull();
  await act(async()=>{finish(running);});
  expect(screen.queryByRole('button',{name:'Stop generating'})).toBeNull();
});
