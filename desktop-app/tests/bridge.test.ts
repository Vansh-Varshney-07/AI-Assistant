import { expect, it, vi } from 'vitest';
import { BackendBridge } from '../src/main/bridge';
it('a failed backend health check cannot keep an old green ready badge', async () => {
  const bridge = new BackendBridge('project', 'host.py', 'runtime');
  bridge.state = { state: 'ready', capabilities: { memory: true } };
  vi.spyOn(bridge, 'call').mockRejectedValue(new Error('Storage unavailable'));
  const state = await bridge.describe();
  expect(state.state).toBe('offline'); expect(state.error).toBe('Storage unavailable');
});
