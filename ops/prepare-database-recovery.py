"""Back up crash-looping stores and validate test-record filtering on copies only."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time
import uuid

project = Path(r'D:\Opencode_\AI assistant')
nonce = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
root = project / '.local' / 'database-recovery' / nonce
root.mkdir(parents=True)
busybox = 'sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662'
test_key = re.compile(rb'^(?:\{?test_|iron_web_2_test_)')

def docker(*args, timeout=120):
    result = subprocess.run(['docker', *map(str, args)], capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Docker operation failed: ' + result.stderr.decode(errors='replace')[:600])
    return result.stdout.decode(errors='replace').strip()

def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def filter_aof(path):
    data = path.read_bytes()
    offset = 0
    chunks = []
    removed = {}
    total = 0
    while offset < len(data):
        start = offset
        end = data.find(b'\r\n', offset)
        if end < 0:
            raise ValueError('Incomplete AOF record header; refusing repair.')
        header = data[offset:end]
        offset = end + 2
        if header.startswith(b'#'):
            chunks.append(data[start:offset])
            continue
        if not header.startswith(b'*'):
            raise ValueError('Unexpected AOF encoding; refusing repair.')
        count = int(header[1:])
        if not 0 < count < 1000000:
            raise ValueError('Invalid AOF argument count.')
        args = []
        for _ in range(count):
            end = data.find(b'\r\n', offset)
            if end < 0 or data[offset:offset+1] != b'$':
                raise ValueError('Invalid AOF bulk header.')
            size = int(data[offset+1:end])
            if size < 0 or end + 2 + size + 2 > len(data):
                raise ValueError('Invalid AOF bulk length.')
            offset = end + 2
            args.append(data[offset:offset+size])
            offset += size
            if data[offset:offset+2] != b'\r\n':
                raise ValueError('Invalid AOF bulk terminator.')
            offset += 2
        total += 1
        # Preserve original bytes for every other command, including binary data.
        if len(args) > 1 and args[0].upper().startswith(b'GRAPH.') and test_key.match(args[1]):
            command = args[0].decode('ascii').upper()
            removed[command] = removed.get(command, 0) + 1
        else:
            chunks.append(data[start:offset])
    before = digest(path)
    if removed:
        path.write_bytes(b''.join(chunks))
    return {'file': path.name, 'original_sha256': before, 'repaired_sha256': digest(path),
            'commands': total, 'removed_test_commands': removed}

configs = json.loads(docker('inspect', 'memory-system-falkordb', 'iron-web-2-falkordb'))
docker('stop', '--time', '20', *[c['Name'].lstrip('/') for c in configs])
report = {'id': nonce, 'originals_modified': False, 'backups': [], 'copies': []}
report_file = root / 'recovery-report.json'

for index, config in enumerate(configs):
    label = 'memory' if index == 0 else 'research'
    directory = root / label
    directory.mkdir()
    mount = next(m for m in config['Mounts'] if m['Destination'] == '/data')
    if mount['Type'] == 'volume':
        source = f"type=volume,source={mount['Name']},target=/source,readonly"
    else:
        source = f"type=bind,source={mount['Source']},target=/source,readonly"
    docker('run', '--rm', '--network', 'none', '--read-only', '--mount', source,
           '--mount', f'type=bind,source={directory},target=/backup',
           '--entrypoint', 'sh', busybox, '-c', 'tar -C /source -cf /backup/data.tar .')
    archive = directory / 'data.tar'
    report['backups'].append({'container': config['Name'].lstrip('/'), 'file': str(archive),
                              'sha256': digest(archive), 'bytes': archive.stat().st_size})
    report_file.write_text(json.dumps(report, indent=2))
    working = directory / 'working'
    working.mkdir()
    with tarfile.open(archive) as tf:
        # The image creates a /data/data compatibility symlink to /data.
        # Retain it in the backup but extract only regular data and directories.
        members = [m for m in tf.getmembers() if m.isfile() or m.isdir()]
        tf.extractall(working, members=members, filter='data')
    files = [filter_aof(p) for p in working.rglob('*.aof')]
    volume = f'ai_assistant_recovery_{label}_{nonce}'.replace('-', '_')
    container = f'ai-assistant-recovery-{label}-{nonce}'
    docker('volume', 'create', '--label', 'ai-assistant-recovery=' + nonce, volume)
    docker('run', '--rm', '--network', 'none', '--read-only',
           '--mount', f'type=bind,source={working},target=/source,readonly',
           '--mount', f'type=volume,source={volume},target=/data',
           '--entrypoint', 'sh', busybox, '-c', 'cp -a /source/. /data/')
    args = ['run', '-d', '--name', container, '--network', 'none',
            '--label', 'ai-assistant-recovery=' + nonce,
            '--mount', f'type=volume,source={volume},target=/data']
    for entry in config['Config']['Env']:
        if entry.split('=', 1)[0] in {'FALKORDB_DATA_PATH', 'REDIS_ARGS', 'FALKORDB_ARGS', 'BROWSER'}:
            args += ['--env', entry]
    args += [config['Config']['Image']]
    docker(*args)
    healthy = False
    for _ in range(45):
        ping = subprocess.run(['docker', 'exec', container, 'redis-cli', 'ping'],
                              capture_output=True, timeout=10)
        if ping.returncode == 0 and ping.stdout.strip() == b'PONG':
            healthy = True
            break
        time.sleep(2)
    graphs = []
    if healthy:
        graphs = docker('exec', container, 'redis-cli', '--raw', 'GRAPH.LIST').splitlines()
    else:
        (directory / 'copy-startup.log').write_text(docker('logs', '--tail', '3000', container))
    record = {'container': config['Name'].lstrip('/'), 'copy_container': container,
              'copy_volume': volume, 'healthy': healthy, 'graph_count': len(graphs),
              'non_test_graph_count': sum(not test_key.match(g.encode()) for g in graphs),
              'aof_files': files}
    report['copies'].append(record)
    report_file.write_text(json.dumps(report, indent=2))
    print(json.dumps({'store': label, 'healthy': healthy, 'graphs': len(graphs),
                      'removed_test_commands': sum(sum(f['removed_test_commands'].values()) for f in files)}), flush=True)
    if not healthy:
        raise RuntimeError('Repaired copy failed validation; originals remain unmodified.')

(project / '.local' / 'latest-database-recovery.txt').write_text(str(report_file))
print('Validated copies and backups recorded at ' + str(report_file))
