import React from 'react';
import {act,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,describe,expect,it,vi} from 'vitest';
import {ConnectionsWorkspace} from '../src/renderer/Connections';
import type {DesktopAPI} from '../src/shared/types';

const backend={state:'ready' as const};
const snapshot=(expires:number)=>({configured:{google:true},checks:{google:{passed:true,label:'Synthetic check',expires}}});
afterEach(()=>vi.useRealTimers());

describe('Connection evidence lifetime and scope',()=>{
  it('expires an observed passing check while the page stays open',async()=>{
    vi.useFakeTimers();vi.setSystemTime(new Date('2026-10-27T00:00:00Z'));
    const api={connectionsStatus:vi.fn(async()=>snapshot(Date.now()/1000+5))} as unknown as DesktopAPI;
    await act(async()=>{render(<ConnectionsWorkspace api={api} space="a" backend={backend}/>);});
    expect(screen.getByText('Live check passed').className).toContain('good');
    await act(async()=>{vi.advanceTimersByTime(5001);});
    expect(screen.queryByText('Live check passed')).toBeNull();
    expect(screen.getByText('Check expired · check again').className).not.toContain('good');
    expect(api.connectionsStatus).toHaveBeenCalledTimes(1); // no hidden provider polling
  });

  it('does not treat a missing expiry or disconnected credential as qualification',async()=>{
    const api={connectionsStatus:async()=>({configured:{google:false,tavily:true},checks:{google:{passed:true,expires:Date.now()/1000+300},tavily:{passed:true}}})} as unknown as DesktopAPI;
    await act(async()=>{render(<ConnectionsWorkspace api={api} space="a" backend={backend}/>);});
    expect(screen.queryByText('Live check passed')).toBeNull();
    expect((screen.getByRole('button',{name:'Read selected Google source'}) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText('Check expired · check again')).toBeTruthy();
  });

  it('ignores an old space response and releases only the current operation lock',async()=>{
    let finishOld!:(value:any)=>void;
    const api={connectionsStatus:vi.fn(async()=>({configured:{google:true},checks:{}})),checkConnection:vi.fn(()=>new Promise(resolve=>{finishOld=resolve;}))} as unknown as DesktopAPI;
    const view=render(<ConnectionsWorkspace api={api} space="a" backend={backend}/>);
    await screen.findByText('Imported · check pending');
    fireEvent.click(screen.getByRole('button',{name:'Check Google connection'}));
    await act(async()=>{view.rerender(<ConnectionsWorkspace api={api} space="b" backend={backend}/>);});
    expect((screen.getByRole('button',{name:'Check Google connection'}) as HTMLButtonElement).disabled).toBe(false);
    await act(async()=>{finishOld(snapshot(Date.now()/1000+300));});
    expect(screen.queryByText('Live check passed')).toBeNull();
    expect(screen.getByText('Imported · check pending')).toBeTruthy();
  });
});
