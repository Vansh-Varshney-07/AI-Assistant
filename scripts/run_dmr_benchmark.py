"""Versioned, question-scoped DMR retrieval; no reader, judge, or provider calls.

Choose question IDs explicitly from a separate development split. Unreviewed
evidence stays unscored; the old converter's final-session labels are not used.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmark_data import dmr_cases, search_case


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def evaluate_case(engine, case, memory_ids, mode, k):
    tick = time.perf_counter()
    try:
        hits = search_case(engine, case, memory_ids, mode=mode, k=k)
        reverse = {value: key for key, value in memory_ids.items()}
        retrieved = [reverse[hit.memory_id] for hit in hits]
        error = None
    except Exception as exc:
        retrieved, error = [], str(exc)
    gold = set(case.gold_evidence)
    return {
        'example_id': case.id, 'condition': mode, 'query': case.question,
        'retrieved_ids': retrieved, 'ground_truth_ids': list(case.gold_evidence),
        'evidence_status': 'reviewed' if gold else 'unannotated; retrieval metrics unavailable',
        'history_documents': len(case.documents),
        'recall1': len(gold & set(retrieved[:1]))/len(gold) if gold else None,
        'recall5': len(gold & set(retrieved[:5]))/len(gold) if gold else None,
        'recall10': len(gold & set(retrieved[:10]))/len(gold) if gold else None,
        'mrr10': next((1/(i+1) for i, mid in enumerate(retrieved[:10]) if mid in gold), 0.) if gold else None,
        'retrieval_ms': 1000*(time.perf_counter()-tick), 'error': error,
        'conversation_id': case.group_id,
    }


def run(args):
    source = Path(args.source)
    requested = json.loads(Path(args.case_ids).read_text(encoding='utf-8'))
    if (not isinstance(requested, list) or not requested
            or any(not isinstance(x, str) for x in requested)
            or len(requested) != len(set(requested))):
        raise ValueError('Choose a nonempty JSON list of distinct question IDs.')
    cases = [case for case in dmr_cases(source, Path(args.evidence) if args.evidence else None)
             if case.id in set(requested)]
    if {case.id for case in cases} != set(requested):
        raise ValueError('Some requested question IDs are absent from the source.')
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    documents = {doc.id: asdict(doc) for case in cases for doc in case.documents}
    (output/'inputs.json').write_text(json.dumps({
        'documents': list(documents.values()),
        'examples': [{'id': c.id, 'group_id': c.group_id, 'question': c.question,
                      'gold_answer': c.gold_answer, 'gold_evidence': c.gold_evidence,
                      'corpus_ids': [d.id for d in c.documents]} for c in cases],
    }, indent=2), encoding='utf-8')
    protocol = {
        'dataset': 'MSC-derived DMR; repaired local protocol v1',
        'source': str(source.resolve()), 'source_sha256': digest(source),
        'case_ids_sha256': digest(args.case_ids), 'question_ids': [c.id for c in cases],
        'evidence_sha256': digest(args.evidence) if args.evidence else None,
        'adapter_sha256': digest(ROOT/'scripts/benchmark_data.py'),
        'runner_sha256': digest(__file__),
        'scope': 'All history sessions in the question conversation, selected before retrieval',
        'conditions': ['vector', 'hybrid'], 'top_k': 10,
        'gold_policy': 'Only source-hash-bound reviewed annotations; no final-session fallback',
        'extraction_policy': 'none', 'provider_calls': 0,
        'status': 'prepared', 'scored_questions': sum(bool(c.gold_evidence) for c in cases),
    }
    protocol_path = output/'protocol.json'
    protocol_path.write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    if not args.run:
        print(f'Prepared {len(cases)} scoped questions; {protocol["scored_questions"]} reviewed evidence sets. {output}')
        return
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    from falkordb import FalkorDB
    from memory.engine import MemoryEngine
    from memory.config import EngineSettings
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    config['extraction_policy'] = 'none'
    config['embeddings']['cache_dir'] = str(ROOT/'.local/benchmarks/models')
    config['reranker']['cache_dir'] = str(ROOT/'.local/benchmarks/models')
    config['retrieval']['reranker_enabled'] = True
    config = EngineSettings.model_validate(config).model_dump()
    name = 'test_dmr_' + uuid.uuid4().hex
    graph = config['falkordb']
    client = FalkorDB(host=graph['host'], port=graph['port'],
                     ssl=graph['tls'], socket_connect_timeout=5, socket_timeout=10)
    owned = False
    try:
        if client.connection.exists(name):
            raise ValueError('Refusing an existing graph namespace.')
        owned = True
        protocol.update(status='running', graph=name, effective_config=config)
        protocol_path.write_text(json.dumps(protocol, indent=2), encoding='utf-8')
        with MemoryEngine(config=config, graph_name=name,
                          qdrant_path=str(output/'qdrant')) as engine:
            memory_ids = {}
            failures = 0
            for doc in documents.values():
                memory_ids[doc['id']] = engine.add(doc['text'], metadata={
                    'benchmark_document_id': doc['id'], 'session_id': doc['session_id']})
            with (output/'retrieval.jsonl').open('w', encoding='utf-8') as handle:
                for case in cases:
                    for mode in protocol['conditions']:
                        row = evaluate_case(engine, case, memory_ids, mode, 10)
                        failures += row['error'] is not None
                        handle.write(json.dumps(row, ensure_ascii=False)+'\n')
                        handle.flush()
        protocol.update(status='complete', retrieval_failures=failures,
                        retrieval_records=2*len(cases))
    except Exception as exc:
        protocol.update(status='failed', error=str(exc))
        raise
    finally:
        protocol_path.write_text(json.dumps(protocol, indent=2), encoding='utf-8')
        if owned:
            if client.connection.exists(name):
                client.select_graph(name).delete()
            client.connection.delete(*['{'+name+'}:'+suffix for suffix in
                                       ('revision', 'lock', 'publication')])
        client.close()
    print(f'Completed paired scoped retrieval: {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='Raw msc_self_instruct.jsonl')
    parser.add_argument('--case-ids', required=True, help='JSON list of explicit development question IDs')
    parser.add_argument('--evidence', help='Reviewed evidence manifest bound to source SHA-256')
    parser.add_argument('--output', required=True, help='New directory; existing runs are never overwritten')
    parser.add_argument('--config', default=str(ROOT/'.local/benchmarks/engine-config.json'))
    parser.add_argument('--run', action='store_true', help='Run local models and an isolated engine; default prepares inputs only')
    run(parser.parse_args())


if __name__ == '__main__':
    main()
