import React from 'react';
import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {Onboarding} from '../src/renderer/Onboarding';
import {localDocker,validModel,SetupManager,DATABASE_IMAGE_ID} from '../src/main/setup';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
it('accepts only local engines and exact public provider fields',()=>{
  expect(localDocker('npipe:////./pipe/dockerDesktopLinuxEngine')).toBe(true);
  for(const v of ['tcp://example.com:2375','ssh://server','npipe:////x/pipe/test'])expect(localDocker(v)).toBe(false);
  expect(validModel({model:'m',provider:'custom',endpoint:'inference.local'})).toBe(true);
  expect(validModel({model:'m',provider:'custom',endpoint:'inference.local',token:'secret'})).toBe(false);
});
it('fresh onboarding cannot finish without actual checks and consent',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'wayfinder-setup-unit-'));
  const setup=new SetupManager(root,path.join(root,'runtime'),'project','absent-backend','models',{} as any,vi.fn());
  await setup.load();expect(setup.ready()).toBe(false);
  expect((await setup.connect()).state).toBe('setup');
  await expect(setup.finish('Personal',true)).rejects.toThrow(/Complete/);
  await expect(setup.finish('Personal',false)).rejects.toThrow(/explicitly/);
});
it('rejects foreign Docker volume without starting or replacing it',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'wayfinder-setup-owner-'));
  const run=vi.fn(async(_file:string,args:string[])=>{
    if(args.join(' ')==='context show')return 'desktop-linux';
    if(args[0]==='context')return JSON.stringify([{Endpoints:{docker:{Host:'npipe:////./pipe/dockerDesktopLinuxEngine'}}}]);
    if(args.includes('version'))return JSON.stringify({Os:'linux'});
    if(args.includes('image'))return DATABASE_IMAGE_ID;
    if(args.includes('volume'))return JSON.stringify([{Labels:{'wayfinder.workspace':'foreign'}}]);
    throw new Error('Unexpected Docker operation');
  });
  const setup=new SetupManager(root,path.join(root,'runtime'),'project','exe','models',{} as any,run);
  await expect(setup.database(false)).rejects.toThrow(/not owned/);
  expect(run.mock.calls.some(([,args])=>args.includes('start')||args.includes('create')||args.includes('rm'))).toBe(false);
});
it('explains disclosure and leaves finish disabled for a new user',async()=>{
  const api={setupStatus:vi.fn(async()=>({storage:'isolated workspace'}))} as any;
  render(<Onboarding api={api} done={vi.fn()}/>);
  await waitFor(()=>expect(api.setupStatus).toHaveBeenCalled());
  expect((screen.getByRole('button',{name:'Create workspace and open Wayfinder'}) as HTMLButtonElement).disabled).toBe(true);
  expect(screen.getByText(/existing Hermes\/OpenShell model connection/)).toBeTruthy();
  expect(screen.getByLabelText(/I agree to send/)).toBeTruthy();
});
