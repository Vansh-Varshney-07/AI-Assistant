"""Offline readiness checks; optional tiny engine check uses only an owned graph.

No provider calls, answer generation, or public-benchmark score is produced.
"""
import argparse
from collections import Counter
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BASE = ROOT / '.local/benchmarks'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


def dataset_checks():
    from benchmark_data import locomo_cases, longmemeval_cases
    result = {}
    for name, cases in [('locomo', locomo_cases())] + [
            ('longmemeval_' + v, longmemeval_cases(v)) for v in ('oracle', 's', 'm')]:
        count, docs, groups, categories = 0, 0, set(), Counter()
        absent = []
        for case in cases:
            count += 1
            assert case.question and case.documents
            assert len({d.id for d in case.documents}) == len(case.documents)
            ids = {d.id if case.evidence_unit == 'dialogue_turn' else d.session_id
                   for d in case.documents}
            missing = set(case.gold_evidence) - ids
            if missing:
                absent.append({'case_id': case.id, 'missing': sorted(missing)})
            categories[case.category] += 1
            if case.group_id not in groups:
                docs += len(case.documents)
                groups.add(case.group_id)
        result[name] = {'cases': count, 'history_groups': len(groups),
                        'documents_across_groups': docs, 'categories': dict(categories),
                        'unmatched_gold_evidence': absent}
        expected = 1986 if name == 'locomo' else 500
        assert count == expected, (name, count)
        print(f'Validated {name}: {count} cases; {len(absent)} unmatched evidence annotations', flush=True)
    return result


def neural_checks():
    from memory.embeddings.embedder import Embedder
    from memory.ranking.reranker import Reranker
    from memory.config import EngineSettings
    model_cache = str(BASE / 'models')
    start = time.perf_counter()
    embedder = Embedder(use_gpu=False, cache_dir=model_cache, batch_size=2)
    reranker = Reranker(use_gpu=False, cache_dir=model_cache, batch_size=2)
    texts = ['Mira prefers green tea without sugar.', 'A bicycle has two wheels.']
    import numpy as np
    embedding = embedder.embed_single(texts[0])
    assert embedding.shape == (384,) and np.isfinite(embedding).all()
    query = 'What does Mira like to drink?'
    ranked = reranker.rerank(query, [{'text': t, 'id': i} for i,t in enumerate(texts)])
    assert ranked[0]['id'] == 0 and all(math.isfinite(x['rerank_score']) for x in ranked)
    assert embedder._providers == ['CPUExecutionProvider']
    assert reranker._providers == ['CPUExecutionProvider']
    config = EngineSettings.model_validate({
        'USE_GPU': False, 'extraction_policy': 'none',
        'embeddings': {'cache_dir': model_cache}, 'reranker': {'cache_dir': model_cache},
        'qdrant': {'path': str(BASE / 'runtime/qdrant')},
        'falkordb': {'graph_name': 'test_benchmark_reserved'},
        'retrieval': {'reranker_enabled': True, 'vector_candidates': 100},
    }).model_dump()
    (BASE/'engine-config.json').write_text(json.dumps(config, indent=2))
    return embedder, reranker, config, {'embedding_dimensions': len(embedding),
        'reranker_model': reranker.model_name, 'embedder_providers': embedder._providers,
        'reranker_providers': reranker._providers, 'finite_scores': True,
        'expected_document_ranked_first': True, 'smoke_seconds': time.perf_counter()-start}


def engine_check(embedder, reranker, config):
    from memory.engine import MemoryEngine
    from falkordb import FalkorDB
    name = 'test_bench_smoke_' + uuid.uuid4().hex
    path = BASE / 'smoke-stores' / name / 'qdrant'
    graph_config = config['falkordb']
    client = FalkorDB(host=graph_config['host'], port=graph_config['port'],
                     socket_connect_timeout=5, socket_timeout=10)
    assert not client.connection.exists(name), 'Refuse any pre-existing graph'
    created = False
    try:
        created = True
        with MemoryEngine(config=config, graph_name=name, qdrant_path=str(path),
                          embedder=embedder, reranker=reranker, use_gpu=False) as engine:
            relevant = engine.add('Mira prefers green tea without sugar.')
            engine.add('A bicycle has two wheels.')
            hits = engine.search('What does Mira like to drink?', k=2, retrieval_mode='hybrid')
            assert hits and hits[0].memory_id == relevant
            assert all(h.retrieval_trace.get('rerank_score') is not None for h in hits)
            return {'passed': True, 'graph': name, 'qdrant_path': str(path),
                    'mode': 'hybrid', 'reranker_enabled': True,
                    'candidate_count': hits[0].retrieval_trace['candidate_count'],
                    'retrieval_traces': [h.retrieval_trace for h in hits],
                    'scope': 'Two synthetic raw episodes; not a benchmark score'}
    finally:
        if created:
            if client.connection.exists(name):
                client.select_graph(name).delete()
            # Only exact UUID-owned auxiliary keys, never application namespaces.
            client.connection.delete(*['{'+name+'}:'+suffix for suffix in
                                     ('revision', 'lock', 'publication')])
        client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--models-only', action='store_true')
    parser.add_argument('--engine-smoke', action='store_true')
    args = parser.parse_args()
    output = BASE / ('model-smoke.json' if args.models_only else 'readiness.json')
    report = {'benchmark_scores_generated': False, 'provider_calls': False,
              'default_application_config_modified': False, 'gpu_verified': False,
              'python': sys.version, 'packages': {d.metadata['Name']: d.version
                                                for d in importlib.metadata.distributions()}}
    if not args.models_only:
        report['datasets'] = dataset_checks()
    embedder, reranker, config, report['models'] = neural_checks()
    output.write_text(json.dumps(report, indent=2))
    if args.engine_smoke:
        try:
            report['engine_smoke'] = engine_check(embedder, reranker, config)
        except Exception as exc:
            report['engine_smoke'] = {'passed': False, 'error': str(exc)}
            output.write_text(json.dumps(report, indent=2))
            raise
    output.write_text(json.dumps(report, indent=2))
    print(f'Readiness report: {output}', flush=True)


if __name__ == '__main__':
    main()
