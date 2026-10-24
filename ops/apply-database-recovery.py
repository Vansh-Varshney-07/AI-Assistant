"""Apply only after explicit approval: pass --scope memory or --scope both."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--scope', choices=['memory', 'both'], required=True)
args = parser.parse_args()
project = Path(r'D:\Opencode_\AI assistant')
report_path = Path((project / '.local/latest-database-recovery.txt').read_text().strip()).resolve()
if not report_path.is_relative_to((project / '.local/database-recovery').resolve()):
    raise SystemExit('Unexpected recovery report path.')
report = json.loads(report_path.read_text())
if not all(c['healthy'] for c in report['copies']):
    raise SystemExit('Recovery copies did not pass validation.')
busybox = 'sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662'

def docker(*command, timeout=120):
    result = subprocess.run(['docker', *map(str, command)], capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Docker operation failed: ' + result.stderr.decode(errors='replace')[:400])
    return result.stdout.decode(errors='replace').strip()

allowed = {'memory-system-falkordb'}
if args.scope == 'both':
    allowed.add('iron-web-2-falkordb')
applied = []
for backup, copy in zip(report['backups'], report['copies']):
    name = copy['container']
    if name not in allowed:
        continue
    archive = Path(backup['file'])
    if hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest() != backup['sha256']:
        raise RuntimeError('Backup checksum mismatch.')
    config = json.loads(docker('inspect', name))[0]
    if config['State']['Running']:
        raise RuntimeError('Original store is running; refusing to modify its persistence files.')
    mount = next(m for m in config['Mounts'] if m['Destination'] == '/data')
    if name == 'memory-system-falkordb':
        if mount['Type'] != 'volume' or mount['Name'] != 'memory_system_falkordb_data':
            raise RuntimeError('Unexpected memory volume.')
        target = f"type=volume,source={mount['Name']},target=/data"
    else:
        expected = Path(r'D:\Opencode_\reserchpaper\Iron_Web_2\data\falkordb').resolve()
        if mount['Type'] != 'bind' or Path(mount['Source']).resolve() != expected:
            raise RuntimeError('Unexpected research database location.')
        target = f"type=bind,source={mount['Source']},target=/data"
    working = archive.parent / 'working'
    for entry in copy['aof_files']:
        if not entry['removed_test_commands']:
            continue
        paths = list(working.rglob(entry['file']))
        if len(paths) != 1:
            raise RuntimeError('Ambiguous repair filename.')
        path = paths[0]
        if hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() != entry['repaired_sha256']:
            raise RuntimeError('Validated repair checksum changed.')
        relative = path.relative_to(working).as_posix()
        # Verify the stopped original still matches its full backup, keep a local
        # pre-repair file, and atomically replace only the filtered AOF file.
        shell = '''set -eu
rel="$1"; expected="$2"; marker="$3"
current="$(sha256sum "/data/$rel")"
test "${current%% *}" = "$expected"
cp -p "/data/$rel" "/data/$rel.before-ai-assistant-$marker"
cp "/repair/$rel" "/data/$rel.ai-assistant-new"
mv "/data/$rel.ai-assistant-new" "/data/$rel"
'''
        docker('run', '--rm', '--network', 'none', '--read-only', '--mount', target,
               '--mount', f'type=bind,source={working},target=/repair,readonly',
               '--entrypoint', 'sh', busybox, '-c', shell, 'sh', relative,
               entry['original_sha256'], report['id'])
    docker('start', name)
    for _ in range(45):
        state = json.loads(docker('inspect', name))[0]['State']
        if state.get('Health', {}).get('Status') == 'healthy':
            break
        time.sleep(2)
    else:
        raise RuntimeError('Original store did not become healthy after repair.')
    applied.append(name)
    print('Recovered and healthy: ' + name, flush=True)
    report['applied_to'] = applied
    report['originals_modified'] = True
    report_path.write_text(json.dumps(report, indent=2))

report['apply_scope'] = args.scope
report['applied_at_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
report_path.write_text(json.dumps(report, indent=2))
print('Backups and pre-repair AOF copies retained; non-test graph commands preserved.')
