import hashlib
import json
from pathlib import Path
import subprocess
import time

names = ['memory-system-falkordb', 'iron-web-2-falkordb']
def docker(*args):
    result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError('Docker verification failed: ' + result.stderr[:250])
    return result.stdout.strip()

def snapshot(name):
    info = json.loads(docker('inspect', name))[0]
    graphs = json.loads(docker('exec', name, 'redis-cli', '--json', 'GRAPH.LIST'))
    return {'healthy': info['State'].get('Health', {}).get('Status') == 'healthy',
            'running': info['State']['Running'], 'restart_count': info['RestartCount'],
            'graph_count': len(graphs),
            'graph_names_sha256': hashlib.sha256(json.dumps(sorted(graphs)).encode()).hexdigest()}

before = {name: snapshot(name) for name in names}
if not all(state['healthy'] for state in before.values()):
    raise RuntimeError('A repaired database was not healthy before restart verification.')
docker('restart', '--time', '20', *names)
for _ in range(45):
    ready = all(json.loads(docker('inspect', name))[0]['State'].get('Health', {}).get('Status') == 'healthy' for name in names)
    if ready:
        break
    time.sleep(2)
else:
    raise RuntimeError('Database health did not recover after restart.')
print('Both databases healthy after restart; observing stability for 30 seconds.', flush=True)
baseline = {name: snapshot(name) for name in names}
time.sleep(30)
after = {name: snapshot(name) for name in names}
passed = all(state['healthy'] and state['running']
             and state['restart_count'] == baseline[name]['restart_count']
             and state['graph_names_sha256'] == before[name]['graph_names_sha256']
             for name, state in after.items())
report = {'passed': passed, 'before': before, 'after_restart': baseline, 'after_stability_window': after}
root = Path(r'D:\Opencode_\AI assistant\.local')
(root / 'database-recovery-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
raise SystemExit(0 if passed else 1)
