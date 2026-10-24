import { readFileSync } from 'node:fs';
import { parseEnv } from 'node:util';
import { spawn } from 'node:child_process';
import { homedir } from 'node:os';

// The credential is read in this process, passed through the child's environment,
// and never included in command arguments or written to this script.
const [mode, keyFile] = process.argv.slice(2);
if (!['models', 'onboard'].includes(mode) || !keyFile) {
  console.error('Usage: node onboard-nvidia.mjs models|onboard /path/to/existing.env');
  process.exit(2);
}
let key;
try { key = parseEnv(readFileSync(keyFile, 'utf8')).NVIDIA_API_KEY; }
catch { console.error('Could not read the authorized credential file.'); process.exit(1); }
if (!key?.trim()) {
  console.error('NVIDIA_API_KEY is absent in the authorized credential file.');
  process.exit(1);
}
key = key.trim();
if (mode === 'models') {
  try {
    const response = await fetch('https://integrate.api.nvidia.com/v1/models', {
      headers: {Authorization: `Bearer ${key}`}, signal: AbortSignal.timeout(30000),
    });
    if (!response.ok) { console.error(`NVIDIA catalog request failed: HTTP ${response.status}`); process.exit(1); }
    const payload = await response.json();
    console.log(JSON.stringify({nemotronModels: (payload.data || [])
      .map(item => item.id).filter(id => typeof id === 'string' && /nemotron/i.test(id))}, null, 2));
  } catch { console.error('NVIDIA catalog request did not complete.'); process.exit(1); }
} else {
  const child = spawn(`${homedir()}/.local/bin/nemohermes`, [
    'onboard', '--name', 'ai-assistant', '--agent', 'hermes',
    '--non-interactive', '--yes', '--no-gpu', '--no-sandbox-gpu',
    '--yes-i-accept-third-party-software',
  ], {stdio: 'inherit', env: {
    ...process.env,
    NEMOCLAW_DISABLE_TELEMETRY: '1', NEMOCLAW_NO_EXPRESS: '1',
    NEMOCLAW_PROVIDER: 'build', NEMOCLAW_AGENT: 'hermes',
    NEMOCLAW_MODEL: 'nvidia/nemotron-3.5-lightning-30b-a3b',
    NEMOCLAW_POLICY_TIER: 'balanced',
    NVIDIA_INFERENCE_API_KEY: key,
  }});
  child.on('error', () => { console.error('Could not start NemoHermes.'); process.exitCode = 1; });
  child.on('exit', code => { process.exitCode = code ?? 1; });
}
