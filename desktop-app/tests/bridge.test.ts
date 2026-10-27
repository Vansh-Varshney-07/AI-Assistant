import { expect, it, vi } from 'vitest';
import { BackendBridge } from '../src/main/bridge';
it('a failed backend health check cannot keep an old green ready badge', async () => {
  const bridge = new BackendBridge('project', 'host.py', 'runtime');
  bridge.state = { state: 'ready', capabilities: { memory: true } };
  vi.spyOn(bridge, 'call').mockRejectedValue(new Error('Storage unavailable'));
  const state = await bridge.describe();
  expect(state.state).toBe('offline'); expect(state.error).toBe('Storage unavailable');
});
it('refuses a mismatched host manifest and closes the owned child', async () => {
  const bridge = new BackendBridge('project', 'host.py', 'runtime');
  // Replace transport launch only; exercise the actual admission check.
  (bridge as any).launch = vi.fn();
  vi.spyOn(bridge, 'call').mockResolvedValue({ state: 'ready', release: { sha256: 'foreign-build' }, instance_generation: 'g' });
  const closed = vi.spyOn(bridge, 'close').mockResolvedValue();
  const state = await bridge.connect();
  expect(state.state).toBe('offline'); expect(state.error).toMatch(/does not match/); expect(closed).toHaveBeenCalledOnce();
});
it('bounds an unfinished response by UTF-8 bytes rather than JavaScript characters', () => {
  const bridge = new BackendBridge('project','host','runtime') as any;
  bridge.child = { kill: vi.fn() };
  bridge.receive('界'.repeat(22000));
  expect(bridge.child.kill).toHaveBeenCalledOnce();
  expect(bridge.buffer).toBe(''); expect(bridge.state.state).toBe('offline');
});
it('parses several valid bounded frames in one chunk without imposing the limit on their sum', () => {
  const bridge = new BackendBridge('project','host','runtime') as any;
  bridge.child = { kill: vi.fn() };
  const first = vi.fn(), second = vi.fn();
  for (const [id,resolve] of [['a',first],['b',second]] as const) bridge.pending.set(id,{resolve,reject:vi.fn(),timer:setTimeout(()=>{},1000)});
  bridge.receive(['a','b'].map(id=>'WAYFINDER_DESKTOP='+JSON.stringify({id,ok:true,data:'x'.repeat(40000)})+'\n').join(''));
  expect(first).toHaveBeenCalledOnce(); expect(second).toHaveBeenCalledOnce(); expect(bridge.child.kill).not.toHaveBeenCalled();
});
it('rejects an oversized command before writing to the owned process', async () => {
  const bridge = new BackendBridge('project','host','runtime') as any;
  bridge.child={stdin:{writable:true,write:vi.fn()}};
  await expect(bridge.call('any',{text:'界'.repeat(22000)})).rejects.toThrow(/limit/);
  expect(bridge.child.stdin.write).not.toHaveBeenCalled();
});
