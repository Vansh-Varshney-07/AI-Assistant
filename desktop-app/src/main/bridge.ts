import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { createHash, randomBytes, randomUUID } from 'node:crypto';
import { existsSync } from 'node:fs';
import path from 'node:path';
import type { BackendState, Row } from '../shared/types';
import release from '../../FEATURES.json';
const releaseHash = createHash('sha256').update(JSON.stringify(release)).digest('hex');

export interface Transport { call(operation: string, body?: Row): Promise<any> }
export class BackendBridge implements Transport {
  private child?: ChildProcessWithoutNullStreams;
  private secret = randomBytes(32).toString('hex');
  private buffer = '';
  private pending = new Map<string, { resolve: (data: any) => void; reject: (error: Error) => void; timer: ReturnType<typeof setTimeout> }>();
  private connecting?: Promise<BackendState>;
  state: BackendState = { state: 'offline' };
  private options: {executable?: string; environment?: NodeJS.ProcessEnv} = {};
  constructor(readonly project: string, readonly host: string, readonly runtime: string, private bootstrapError?: string) {}
  configure(options: {executable: string; environment: NodeJS.ProcessEnv}) {
    if (this.child) throw new Error('Close the current backend before changing its private connection.');
    this.options=options;
  }
  async connect(): Promise<BackendState> {
    if (this.connecting) return this.connecting;
    if (this.state.state === 'ready') return this.state;
    this.state = { state: 'starting' };
    this.connecting = (async () => {
      try {
        if (this.bootstrapError) throw new Error(this.bootstrapError);
        if (!this.child) this.launch();
        this.state = await this.call('boot', {}, 120000);
        if (this.state.release?.sha256 !== releaseHash || typeof this.state.instance_generation !== 'string' || !this.state.instance_generation) {
          await this.close();
          throw new Error('The owned host does not match this build manifest. No operation was enabled. Rebuild or select the matching project.');
        }
      } catch (error) {
        this.state = { state: 'offline', runtime: this.runtime, error: error instanceof Error ? error.message : 'Backend is unavailable.' };
      } finally { this.connecting = undefined; }
      return this.state;
    })();
    return this.connecting;
  }
  private launch() {
    const candidates = [process.env.WAYFINDER_PYTHON, path.join(this.project, '.venv', 'Scripts', 'python.exe'), path.resolve(this.project, '..', 'reserchpaper', '.venv', 'Scripts', 'python.exe')];
    const python = this.options.executable || candidates.find(p => p && existsSync(p));
    if (!python) throw new Error('Configured Python environment missing. Set WAYFINDER_PYTHON to the existing project environment; nothing was installed automatically.');
    this.child = spawn(python, [...(this.options.executable ? [] : ['-B', '-u', this.host]), '--project', this.project, '--runtime', this.runtime], {
      cwd: this.project, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, ...this.options.environment, WAYFINDER_HOST_SECRET: this.secret, PYTHONDONTWRITEBYTECODE: '1', HF_HUB_OFFLINE: '1', TRANSFORMERS_OFFLINE: '1' },
    });
    this.child.stdout.setEncoding('utf8');
    this.child.stdout.on('data', (chunk: string) => this.receive(chunk));
    this.child.stderr.on('data', () => {}); // Libraries may log private paths; never forward them to a renderer/log.
    this.child.on('error', () => this.stopped('Could not start the owned backend process.'));
    this.child.on('exit', () => { this.child = undefined; this.stopped('Backend disconnected. Existing operations were not retried.'); });
  }
  private stopped(message: string) {
    this.state = { state: 'offline', error: message, runtime: this.runtime };
    for (const p of this.pending.values()) { clearTimeout(p.timer); p.reject(new Error(message)); }
    this.pending.clear();
  }
  private receive(chunk: string) {
    this.buffer += chunk;
    let newline: number;
    while ((newline = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, newline); this.buffer = this.buffer.slice(newline + 1);
      if (Buffer.byteLength(line, 'utf8') + 1 > 65536) { this.child?.kill(); this.buffer = ''; this.stopped('Backend response exceeded the bounded transport.'); return; }
      if (!line.startsWith('WAYFINDER_DESKTOP=')) continue;
      try {
        const value = JSON.parse(line.slice('WAYFINDER_DESKTOP='.length));
        if (!value || typeof value.id !== 'string' || typeof value.ok !== 'boolean' || Object.keys(value).some(key => !['id','ok','data','error'].includes(key))) throw new Error('Invalid response envelope');
        const p = this.pending.get(value.id); if (!p) continue;
        this.pending.delete(value.id); clearTimeout(p.timer);
        value.ok ? p.resolve(value.data) : p.reject(new Error(typeof value.error === 'string' ? value.error : 'Backend rejected the request.'));
      } catch { this.child?.kill(); this.buffer = ''; this.stopped('Invalid backend transport response.'); return; }
    }
    if (Buffer.byteLength(this.buffer, 'utf8') > 65536) { this.child?.kill(); this.buffer = ''; this.stopped('Backend response exceeded the bounded transport.'); }
  }
  call(operation: string, body: Row = {}, timeout = 40000): Promise<any> {
    const child = this.child; if (!child?.stdin.writable) return Promise.reject(new Error('Backend offline. Retry connection in Settings.'));
    if (this.pending.size >= 16) return Promise.reject(new Error('Too many pending requests. Wait for current work.'));
    const id = randomUUID();
    const raw = JSON.stringify({ id, secret: this.secret, operation, body }) + '\n';
    if (Buffer.byteLength(raw) > 65536) return Promise.reject(new Error('Request exceeds the desktop limit.'));
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error('Request timed out; outcome may be unconfirmed. Inspect Runs before trying any effect again.')); }, timeout);
      this.pending.set(id, { resolve, reject, timer });
      child.stdin.write(raw, error => { if (error) { this.pending.delete(id); clearTimeout(timer); reject(new Error('Backend disconnected; request was not retried.')); } });
    });
  }
  async describe(): Promise<BackendState> {
    if (this.state.state !== 'ready') return this.state;
    try { this.state = await this.call('describe'); }
    catch (error) { this.state = { state: 'offline', runtime: this.runtime, error: error instanceof Error ? error.message : 'Backend health check failed.' }; }
    return this.state;
  }
  async close() {
    const child = this.child; if (!child) return;
    child.stdin.end(JSON.stringify({ id: randomUUID(), secret: this.secret, operation: 'shutdown', body: {} }) + '\n');
    await new Promise<void>(resolve => {
      const timer = setTimeout(() => { child.kill(); resolve(); }, 12000);
      child.once('exit', () => { clearTimeout(timer); resolve(); });
    });
  }
}
