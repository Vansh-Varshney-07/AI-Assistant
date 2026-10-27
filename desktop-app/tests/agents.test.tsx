import React from 'react';
import {render,screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {expect,it,vi} from 'vitest';
import {AgentsPanel} from '../src/renderer/Agents';
import type {DesktopAPI} from '../src/shared/types';
function setup(){
  const api={profiles:vi.fn(async()=>({version:'1',profiles:[{id:'A05',name:'Knowledge & Learning',execution:{included:true,available:true,status:'ready_for_selected_file',note:'Selected file only'}},{id:'A08',name:'Fitness & Habits',execution:{included:false,available:false,status:'deferred',note:'Fitness deferred'}}],presets:[{id:'P01',name:'Google Workspace Assistant',lead:'A02',helpers:[],required_connections:['calendar']}]})),profileTasks:vi.fn(async()=>[]),startProfileTask:vi.fn(async()=>({id:'task',profile_id:'A05',status:'completed',goal:'study',result:{text:'Source-linked fixture guide',sources:[{name:'test.md',reference:'r',sha256:'abc',truncated:false}]},metrics:{worker_invocations:1,delegations:0}}))};
  const props={space:'a',api:api as unknown as DesktopAPI,busy:false,act:async(job:()=>Promise<any>,then?:(r:any)=>void)=>{then?.(await job());},files:{files:[{id:'r',name:'test.md',bytes:40}]},setFiles:vi.fn(),go:vi.fn()};
  render(<AgentsPanel {...props}/>);return{api,props};
}
it('executes one explicit selected-file task and shows the actual attributed artifact',async()=>{
  const {api}=setup();await screen.findByText('Knowledge & Learning');
  await userEvent.click(screen.getByRole('button',{name:'Run selected-file task'}));
  await screen.findByText('Source-linked fixture guide');
  expect(api.startProfileTask).toHaveBeenCalledWith('a','A05','r',expect.stringContaining('study guide'));
  expect(screen.getByText('test.md',{selector:'.observation strong'})).toBeTruthy();
});
it('deferred Fitness has no execution fallback and provider presets do not claim connection',async()=>{
  const {api}=setup();await screen.findByText('Fitness & Habits');
  await userEvent.click(screen.getByRole('button',{name:/A08 Fitness & Habits/}));
  expect(screen.queryByRole('button',{name:'Run selected-file task'})).toBeNull();
  expect(api.startProfileTask).not.toHaveBeenCalled();expect(screen.getByText('Agent workflow unqualified')).toBeTruthy();
});
