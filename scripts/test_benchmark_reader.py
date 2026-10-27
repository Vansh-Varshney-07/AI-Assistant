"""Offline regression checks for paired replay protocol and context limits."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from collect_paper_tables import local_qa, READER_PROMPTS, validate_qa_checkpoint


class ReaderTests(unittest.TestCase):
    def test_replay_applies_top_k_budget_and_prompt_to_both_conditions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root/'report/full20_graph_analysis_20261013'
            (base/'raw').mkdir(parents=True)
            jobs = {}
            for benchmark in ('dmr', 'locomo', 'longmemeval'):
                source = root/(benchmark+'.json')
                source.write_text(json.dumps({'documents': [
                    {'doc_id': f'd{i}', 'text': 'history '*20} for i in range(12)]}), encoding='utf-8')
                jobs[benchmark] = {'input': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
                record = {'example_id': 'q', 'query': 'question', 'gold_answer': 'answer',
                          'retrieved_ids': [f'd{i}' for i in range(12)]}
                for profile in ('vector', 'reranked_hybrid'):
                    (base/'raw'/f'{benchmark}_{profile}_falkordb_after.jsonl').write_text(
                        json.dumps(record)+'\n', encoding='utf-8')
            (base/'verified_summary.json').write_text(json.dumps({'jobs': jobs}), encoding='utf-8')
            generated = []
            def reader(request, **kwargs):
                path = request.full_url.split('3397')[-1]
                payload = json.loads(request.data) if request.data else None
                if path == '/health':
                    result = {'status': 'ok'}
                elif path == '/tokenize':
                    result = {'tokens': list(payload['content'].encode())}
                elif path == '/detokenize':
                    result = {'content': bytes(payload['tokens']).decode()}
                else:
                    self.assertEqual(path, '/v1/chat/completions')
                    generated.append(payload)
                    result = {'choices': [{'message': {'content': 'answer'}, 'finish_reason': 'stop'}]}
                return io.BytesIO(json.dumps(result).encode())
            args = SimpleNamespace(reader_url='http://127.0.0.1:3397', output=str(root/'out'),
                archive_root=str(root), qa_limit=0, context_tokens=1800,
                top_k_documents=10, reader_prompt='concise', seed=1)
            with patch('collect_paper_tables.urlopen', side_effect=reader):
                local_qa(args)
                local_qa(args)  # A resume must not generate duplicates.
                args.reader_prompt = 'legacy'
                with self.assertRaisesRegex(ValueError, 'protocol mismatch'):
                    local_qa(args)
            self.assertEqual(len(generated), 6)
            self.assertEqual({r['messages'][0]['content'] for r in generated}, {READER_PROMPTS['concise']})
            rows = [json.loads(line) for line in (root/'out/local_qa_predictions.jsonl').read_text().splitlines()]
            self.assertTrue(all(len(r['retrieved_ids']) == 10 for r in rows))
            self.assertTrue(all(r['context_token_count'] <= 1800 for r in rows))
            self.assertTrue(all('Excerpt 10:' in r['context'] for r in rows))

    def test_legacy_cache_only_accepts_exact_legacy_protocol(self):
        old = dict(reader='reader', runtime='runtime', temperature=0, seed=1,
                   context_tokens=768, top_k_documents=5, max_generated_tokens=48,
                   sources=[], excluded=[])
        policy = {**old, 'prompt': READER_PROMPTS['legacy']}
        validate_qa_checkpoint(old, policy)
        for key, value in [('context_tokens', 1800), ('top_k_documents', 10),
                           ('prompt', READER_PROMPTS['concise']), ('max_generated_tokens', 64)]:
            changed = copy.deepcopy(policy)
            changed[key] = value
            with self.assertRaises(ValueError):
                validate_qa_checkpoint(old, changed)


if __name__ == '__main__':
    unittest.main()
