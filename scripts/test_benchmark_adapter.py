"""Small offline checks for annotation separation and source-history fidelity."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from benchmark_data import dmr_cases, search_case, locomo_cases, longmemeval_cases
from run_dmr_benchmark import evaluate_case


class AdapterTests(unittest.TestCase):
    def fixture(self, data):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / 'fixture.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def dmr_fixture(self):
        row = {'dialog': [{'id': 'A', 'text': 'Later history'}],
               'previous_dialogs': [{'dialog': [{'id': 'B', 'text': 'Earlier history'}]}],
               'self_instruct': {'B': '__QUESTION_ONLY__', 'A': '__GOLD_ONLY__'},
               'summary_speaker_1': '__SUMMARY_ONLY__'}
        path = self.fixture(row)
        path.write_text(json.dumps(row)+'\n\n'+json.dumps(row), encoding='utf-8')
        return path

    def test_dmr_preserves_histories_without_inventing_gold(self):
        cases = list(dmr_cases(self.dmr_fixture()))
        self.assertEqual([c.id for c in cases], ['dmr:0000:qa', 'dmr:0001:qa'])
        self.assertEqual(cases[0].gold_evidence, ())
        self.assertEqual([d.text for d in cases[0].documents],
                         ['B: Earlier history', 'A: Later history'])
        self.assertNotIn('__GOLD_ONLY__', str(cases[0].documents))
        self.assertNotIn('__SUMMARY_ONLY__', str(cases[0].documents))

    def test_dmr_reviewed_annotations_require_source_hash_and_own_history(self):
        source = self.dmr_fixture()
        annotation = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'annotations': {'dmr:0000:qa': {
                          'document_ids': ['dmr:0000:session:0'],
                          'reviewer': 'fixture', 'rationale': 'Fixture evidence is in the first session'}}}
        path = self.fixture(annotation)
        self.assertEqual(next(dmr_cases(source, path)).gold_evidence, ('dmr:0000:session:0',))
        annotation['annotations']['dmr:0000:qa']['document_ids'] = ['dmr:0001:session:0']
        path.write_text(json.dumps(annotation), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Invalid reviewed'):
            list(dmr_cases(source, path))
        annotation['source_sha256'] = 'wrong'
        path.write_text(json.dumps(annotation), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'different source'):
            list(dmr_cases(source, path))

    def test_both_conditions_scope_before_search_and_unannotated_metrics_stay_null(self):
        case = next(dmr_cases(self.dmr_fixture()))
        mapping = {d.id: f'memory-{i}' for i, d in enumerate(case.documents)}
        mapping['foreign-doc'] = 'foreign-memory'
        calls = []
        def search(query, **kwargs):
            calls.append(kwargs)
            return [SimpleNamespace(memory_id='memory-0')]
        engine = SimpleNamespace(search=search)
        for mode in ('vector', 'hybrid'):
            row = evaluate_case(engine, case, mapping, mode, 10)
            self.assertIsNone(row['recall5'])
            self.assertIsNone(row['recall1'])
            self.assertIsNone(row['mrr10'])
            self.assertIsNone(row['error'])
        self.assertEqual([x['document_ids'] for x in calls],
                         [['memory-0', 'memory-1']]*2)
        engine.search = lambda *a, **kw: [SimpleNamespace(memory_id='foreign-memory')]
        with self.assertRaisesRegex(ValueError, 'outside'):
            search_case(engine, case, mapping, mode='hybrid')

    def test_dmr_retrieval_failure_is_zero_when_evidence_is_reviewed(self):
        from dataclasses import replace
        case = next(dmr_cases(self.dmr_fixture()))
        case = replace(case, gold_evidence=(case.documents[0].id,))
        mapping = {d.id: str(i) for i, d in enumerate(case.documents)}
        def fail(*args, **kwargs):
            raise RuntimeError('synthetic retrieval failure')
        row = evaluate_case(SimpleNamespace(search=fail), case, mapping, 'vector', 10)
        self.assertEqual(row['recall1'], 0.)
        self.assertEqual(row['recall5'], 0.)
        self.assertEqual(row['mrr10'], 0.)
        self.assertEqual(row['error'], 'synthetic retrieval failure')

    def test_locomo_only_ingests_history_not_gold_or_summaries(self):
        path = self.fixture([{'sample_id': 'x', 'conversation': {
            'session_1_date_time': 'date', 'session_1': [
                {'dia_id': 'D1:1', 'speaker': 'A', 'text': 'HISTORY'}]},
            'observation': '__SUMMARY_ONLY__', 'qa': [{'question': '__QUESTION_ONLY__',
            'answer': '__GOLD_ONLY__', 'category': 1, 'evidence': ['D1:1']},
            {'question': 'abstain', 'category': 5, 'evidence': []}]}])
        cases = list(locomo_cases(path))
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0].documents[0].text, 'Date: date\nA: HISTORY')
        self.assertEqual(cases[0].gold_evidence, ('D1:1',))
        self.assertIsNone(cases[1].gold_answer)
        self.assertEqual(cases[1].category, '5')

    def long_sample(self):
        return {'question_id': 'q', 'question': '__QUESTION_ONLY__', 'question_date': 'now',
                'question_type': 'knowledge-update', 'answer': '__GOLD_ONLY__',
                'answer_session_ids': ['same'], 'haystack_session_ids': ['same','same'],
                'haystack_dates': ['first','later'], 'haystack_sessions': [
                    [{'role': 'user', 'content': 'HISTORY', 'has_answer': True}],
                    [{'role': 'assistant', 'content': 'SECOND', 'has_answer': False}]]}

    def test_longmemeval_preserves_duplicate_session_occurrences_without_label_leakage(self):
        case = next(longmemeval_cases('s', self.fixture([self.long_sample()])))
        self.assertEqual(len({d.id for d in case.documents}), 2)
        self.assertEqual([d.session_id for d in case.documents], ['same','same'])
        self.assertEqual(case.documents[0].text, 'Date: first\nuser: HISTORY')
        self.assertNotIn('has_answer', str(case.documents))
        self.assertNotIn('__GOLD_ONLY__', str(case.documents))
        self.assertNotIn('__QUESTION_ONLY__', str(case.documents))

    def test_longmemeval_rejects_misaligned_arrays(self):
        sample = self.long_sample()
        sample['haystack_dates'] = []
        with self.assertRaises(ValueError):
            next(longmemeval_cases('s', self.fixture([sample])))

    def test_longmemeval_requires_explicit_known_variant(self):
        with self.assertRaises(ValueError):
            next(longmemeval_cases('unknown'))


if __name__ == '__main__':
    unittest.main()
