"""Download pinned official data and ONNX models; never open application stores.

Run with .local/benchmarks/.venv/Scripts/python.exe after installing
requirements/benchmarks.txt. Reruns reuse the saved revision lock and files.
"""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/benchmarks'
BASE.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': 'IronWeb-local-benchmark-setup/1.0'}


def api(url):
    with urlopen(Request(url, headers=HEADERS), timeout=60) as response:
        return json.load(response)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def download(url, path, size=None, digest=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (size is None or path.stat().st_size == size):
        actual = sha256(path)
        if digest is None or actual == digest:
            return {'path': str(path.relative_to(BASE)), 'url': url,
                    'bytes': path.stat().st_size, 'sha256': actual}
    partial = path.with_name(path.name + '.partial')
    for attempt in range(3):
        try:
            offset = partial.stat().st_size if partial.exists() else 0
            headers = dict(HEADERS)
            if offset:
                headers['Range'] = f'bytes={offset}-'
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                if response.status != 206:
                    offset = 0
                last = time.monotonic()
                print(f'Downloading {path.name} (resume={offset})', flush=True)
                with partial.open('ab' if offset else 'wb') as handle:
                    while chunk := response.read(4 * 1024 * 1024):
                        handle.write(chunk)
                        offset += len(chunk)
                        if time.monotonic() - last > 15:
                            print(f'{path.name}: {offset / 1e6:.1f} MB', flush=True)
                            last = time.monotonic()
            if size is not None and partial.stat().st_size != size:
                raise ValueError(f'Incomplete download: {path.name}')
            actual = sha256(partial)
            if digest is not None and actual != digest:
                partial.unlink()
                raise ValueError(f'SHA-256 mismatch: {path.name}')
            partial.replace(path)
            print(f'Verified {path.name}: {path.stat().st_size / 1e6:.1f} MB', flush=True)
            return {'path': str(path.relative_to(BASE)), 'url': url,
                    'bytes': path.stat().st_size, 'sha256': actual}
        except Exception as exc:
            print(f'{path.name}: attempt {attempt + 1} failed: {exc}', flush=True)
            if attempt == 2:
                raise
            time.sleep(2)


def revisions():
    lock = BASE / 'revisions.json'
    if lock.exists():
        return json.loads(lock.read_text())
    value = {
        'locomo': api('https://api.github.com/repos/snap-research/locomo/commits/main')['sha'],
        'longmemeval_code': api('https://api.github.com/repos/xiaowu0162/LongMemEval/commits/main')['sha'],
        'longmemeval_data': api('https://huggingface.co/api/datasets/xiaowu0162/longmemeval-cleaned')['sha'],
        'reranker': api('https://huggingface.co/api/models/BAAI/bge-reranker-base')['sha'],
        'embedder': api('https://huggingface.co/api/models/qdrant/bge-small-en-v1.5-onnx-q')['sha'],
    }
    lock.write_text(json.dumps(value, indent=2))
    return value


def github_sources(repo, revision, key, wanted):
    tree = api(f'https://api.github.com/repos/{repo}/git/trees/{revision}?recursive=1')['tree']
    files = []
    for item in tree:
        name = item['path']
        if item['type'] != 'blob' or not wanted(name):
            continue
        files.append(download(f'https://raw.githubusercontent.com/{repo}/{revision}/{name}',
                              BASE / 'sources' / key / name, size=item.get('size')))
    return {'kind': key, 'repository': repo, 'revision': revision, 'files': files}


def locomo(rev):
    return github_sources('snap-research/locomo', rev['locomo'], 'locomo',
                          lambda n: n in ('data/locomo10.json', 'LICENSE.txt', 'README.MD')
                          or (n.startswith('task_eval/') and n.endswith('.py')))


def longmemeval(rev):
    source = github_sources('xiaowu0162/LongMemEval', rev['longmemeval_code'], 'longmemeval',
                            lambda n: n.lower().startswith(('license', 'readme'))
                            or (n.endswith('.py') and ('evaluation' in n or 'evaluate' in n)))
    repository = 'xiaowu0162/longmemeval-cleaned'
    revision = rev['longmemeval_data']
    tree = api(f'https://huggingface.co/api/datasets/{repository}/tree/{revision}')
    files = []
    for item in tree:
        name = item['path']
        if name not in ('README.md', 'longmemeval_oracle.json', 'longmemeval_s_cleaned.json', 'longmemeval_m_cleaned.json'):
            continue
        files.append(download(f'https://huggingface.co/datasets/{repository}/resolve/{revision}/{name}',
                              BASE / 'datasets/longmemeval' / name,
                              item['size'], item.get('lfs', {}).get('oid')))
    return {'kind': 'longmemeval', 'repository': repository, 'revision': revision,
            'files': files, 'evaluation_sources': source}


def model(repo, revision, model_file):
    tree = api(f'https://huggingface.co/api/models/{repo}/tree/{revision}?recursive=true')
    cache = BASE / 'models' / ('models--' + repo.replace('/', '--'))
    snapshot = cache / 'snapshots' / revision
    names = {'config.json', 'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json',
             'preprocessor_config.json', 'vocab.txt', 'README.md', 'LICENSE', 'LICENSE.txt', model_file}
    files = []
    for item in tree:
        name = item['path']
        if item['type'] != 'file' or not (name in names or name.startswith(model_file + '_')):
            continue
        files.append(download(f'https://huggingface.co/{repo}/resolve/{revision}/{name}',
                              snapshot / name, item['size'], item.get('lfs', {}).get('oid')))
    assert (snapshot / model_file).is_file(), 'Missing actual ONNX weights'
    (cache / 'refs').mkdir(parents=True, exist_ok=True)
    (cache / 'refs/main').write_text(revision)
    return {'kind': 'model', 'repository': repo, 'revision': revision, 'files': files,
            'snapshot': str(snapshot.relative_to(BASE)), 'execution': 'CPU; no remote code'}


def main():
    rev = revisions()
    jobs = [lambda: locomo(rev), lambda: longmemeval(rev),
            lambda: model('BAAI/bge-reranker-base', rev['reranker'], 'onnx/model.onnx'),
            lambda: model('qdrant/bge-small-en-v1.5-onnx-q', rev['embedder'], 'model_optimized.onnx')]
    result = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for future in concurrent.futures.as_completed([pool.submit(job) for job in jobs]):
            result.append(future.result())
            (BASE / 'download-manifest.json').write_text(json.dumps({'revisions': rev, 'downloads': result}, indent=2))
    print('All benchmark data and model downloads completed.', flush=True)


if __name__ == '__main__':
    main()
