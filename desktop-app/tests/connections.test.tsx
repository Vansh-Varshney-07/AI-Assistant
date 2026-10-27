import React from 'react';
import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {ConnectionsWorkspace} from '../src/renderer/Connections';
const ready={state:'ready' as const};
function api(){return {connectionsStatus:vi.fn(async()=>({configured:{google:true,tavily:true,notion:true},checks:{}})),importConnections:vi.fn(async()=>null),checkConnection:vi.fn(async()=>({configured:{google:true},checks:{google:{passed:true,label:'Calendar, Tasks and Gmail reads verified',expires:Date.now()/1000+300}}})),googleGrant:vi.fn(async()=>({id:'g'})),googleRead:vi.fn(async()=>({records:[],possibly_truncated:false})),googleRevoke:vi.fn(async()=>({revoked:true})),externalGrant:vi.fn(async()=>({id:'t'})),externalRead:vi.fn(async()=>({provider:'tavily',records:[{id:'1',title:'<script>not executable</script>',content:'Synthetic result',url:'https://example.com'}]})),externalRevoke:vi.fn(async()=>({revoked:true})),disconnectConnection:vi.fn(async()=>({configured:{},checks:{}}))} as any;}
it('uses scoped grants for reads and revokes them after observing results',async()=>{
  const client=api();render(<ConnectionsWorkspace api={client} backend={ready} space="owned"/>);await waitFor(()=>expect(client.connectionsStatus).toHaveBeenCalledWith('owned'));
  await screen.findAllByText('Imported · check pending');
  fireEvent.change(screen.getByLabelText('Web search query'),{target:{value:'synthetic query'}});fireEvent.click(screen.getByRole('button',{name:'Search web'}));
  await screen.findByText('Synthetic result');expect(client.externalGrant).toHaveBeenCalledWith('owned',{provider:'tavily',intent:'search',query:'synthetic query'});expect(client.externalRevoke).toHaveBeenCalledWith('owned','t');expect(document.querySelector('script')).toBeNull();
});
it('qualifies a connection instead of equating imported keys with availability',async()=>{
  const client=api();render(<ConnectionsWorkspace api={client} backend={ready} space="owned"/>);await screen.findAllByText('Imported · check pending');fireEvent.click(screen.getByRole('button',{name:'Check Google connection'}));await screen.findByText('Live check passed');expect(client.checkConnection).toHaveBeenCalledWith('owned','google');
});
it('selects Google sources by an unambiguous accessible name and binds the selected resource',async()=>{
  const client=api();render(<ConnectionsWorkspace api={client} backend={ready} space="owned"/>);await screen.findAllByText('Imported · check pending');
  fireEvent.change(screen.getByRole('combobox',{name:'Google source'}),{target:{value:'contacts'}});
  fireEvent.click(screen.getByRole('button',{name:'Read selected Google source'}));await screen.findByText('No matching records. Nothing was invented.');
  expect(client.googleGrant).toHaveBeenCalledWith('owned',{service:'contacts',resource:'me',limit:3});expect(client.googleRevoke).toHaveBeenCalledWith('owned','g');
});
it('clears old account results on a space change and ignores a late response',async()=>{
  const client=api();let finish:(v:any)=>void=()=>{};client.googleRead.mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
  const view=render(<ConnectionsWorkspace api={client} backend={ready} space="first"/>);await waitFor(()=>expect((screen.getByRole('button',{name:'Read selected Google source'}) as HTMLButtonElement).disabled).toBe(false));fireEvent.click(screen.getByRole('button',{name:'Read selected Google source'}));await waitFor(()=>expect(client.googleRead).toHaveBeenCalled());view.rerender(<ConnectionsWorkspace api={client} backend={ready} space="second"/>);finish({records:[{id:'private',title:'FIRST_SPACE_PRIVATE'}]});await waitFor(()=>expect(client.connectionsStatus).toHaveBeenCalledWith('second'));expect(screen.queryByText('FIRST_SPACE_PRIVATE')).toBeNull();
});
