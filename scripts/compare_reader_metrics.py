"""Compare fixed reader protocols on exactly matched archived question pairs."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from collect_paper_tables import BENCHMARKS, LABELS, answer_scores, exact_mcnemar, holm


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def pairs(path):
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    indexed = {(row['benchmark'], row['example_id']): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError('Duplicate question pairs')
    return indexed


def compare(before, after):
    old_policy, new_policy = [load(folder/'local_qa_protocol.json') for folder in (before, after)]
    for key in ('reader', 'runtime', 'temperature', 'seed', 'max_generated_tokens',
                'sources', 'excluded', 'scoring'):
        if old_policy[key] != new_policy[key]:
            raise ValueError(f'Unmatched comparison setting: {key}')
    if all((folder/'reader_runtime_proof.json').exists() for folder in (before, after)):
        proofs = [load(folder/'reader_runtime_proof.json') for folder in (before, after)]
        for key in ('model_sha256', 'server_build'):
            if proofs[0][key] != proofs[1][key]:
                raise ValueError(f'Reader runtime changed: {key}')
    old, new = [pairs(folder/'local_qa_pairs.jsonl') for folder in (before, after)]
    if not old or set(old) != set(new):
        raise ValueError('Before/after question identities must match exactly')
    changes, rows = [], []
    for identity in old:
        left, right = old[identity], new[identity]
        for key in ('query', 'gold_answer', 'reader_model', 'grading_protocol'):
            if left[key] != right[key]:
                raise ValueError(f'Unmatched question field {key}: {identity}')
        for condition in ('ironweb', 'baseline'):
            for record in (left, right):
                scored = answer_scores(record[condition+'_prediction'], record['gold_answer'])
                correct = record[condition+'_correct']
                if not isinstance(correct, bool):
                    raise ValueError('Correctness must be boolean')
                if not record[condition+'_error']:
                    if correct != scored['exact_match'] or not math.isclose(
                            record[condition+'_token_f1'], scored['token_f1'], abs_tol=1e-12):
                        raise ValueError('Saved scores disagree with independent recomputation')
                elif correct or record[condition+'_token_f1'] != 0:
                    raise ValueError('Generation failures must remain incorrect')
            changes.append({
                'benchmark': identity[0], 'example_id': identity[1], 'condition': condition,
                'old_correct': left[condition+'_correct'], 'new_correct': right[condition+'_correct'],
                'old_f1': left[condition+'_token_f1'], 'new_f1': right[condition+'_token_f1'],
                'old_error': left[condition+'_error'], 'new_error': right[condition+'_error'],
            })
    for benchmark in BENCHMARKS:
        for condition in ('ironweb', 'baseline'):
            cohort = [r for r in changes if r['benchmark'] == benchmark and r['condition'] == condition]
            n = len(cohort)
            if not n:
                continue
            wins = sum(r['new_correct'] and not r['old_correct'] for r in cohort)
            losses = sum(r['old_correct'] and not r['new_correct'] for r in cohort)
            old_correct, new_correct = [sum(r[key] for r in cohort) for key in ('old_correct', 'new_correct')]
            old_f1, new_f1 = [100*statistics.mean(r[key] for r in cohort) for key in ('old_f1', 'new_f1')]
            rows.append({
                'benchmark': benchmark, 'condition': condition, 'n': n,
                'old_correct': old_correct, 'new_correct': new_correct,
                'old_em_percent': 100*old_correct/n, 'new_em_percent': 100*new_correct/n,
                'em_delta_pp': 100*(new_correct-old_correct)/n,
                'old_f1_percent': old_f1, 'new_f1_percent': new_f1, 'f1_delta_pp': new_f1-old_f1,
                'wins': wins, 'losses': losses, 'p_exact': exact_mcnemar(wins, losses),
                'old_errors': sum(bool(r['old_error']) for r in cohort),
                'new_errors': sum(bool(r['new_error']) for r in cohort),
            })
    for row, adjusted in zip(rows, holm([r['p_exact'] for r in rows])):
        row['p_holm_six_comparisons'] = adjusted
    totals = []
    for condition in ('ironweb', 'baseline'):
        cohort = [r for r in changes if r['condition'] == condition]
        n = len(cohort)
        old_correct, new_correct = [sum(r[key] for r in cohort) for key in ('old_correct', 'new_correct')]
        totals.append({'condition': condition, 'n': n, 'old_correct': old_correct,
                       'new_correct': new_correct, 'old_em_percent': 100*old_correct/n,
                       'new_em_percent': 100*new_correct/n,
                       'em_delta_pp': 100*(new_correct-old_correct)/n,
                       'old_f1_percent': 100*statistics.mean(r['old_f1'] for r in cohort),
                       'new_f1_percent': 100*statistics.mean(r['new_f1'] for r in cohort)})
    hashes = {}
    for label, folder in [('before', before), ('after', after)]:
        hashes[label] = {}
        for name in ('local_qa_protocol.json', 'local_qa_pairs.jsonl', 'local_qa_predictions.jsonl'):
            with (folder/name).open('rb') as handle:
                hashes[label][name] = hashlib.file_digest(handle, 'sha256').hexdigest()
    result = {'before': str(before.resolve()), 'after': str(after.resolve()),
              'matched_pairs': len(old), 'comparison': 'Fixed bundled reader change on archived rankings',
              'rows': rows, 'totals_descriptive': totals, 'source_hashes': hashes,
              'limits': ['Question-level tests share histories; independence is limited.',
                         'No parameter selection or individual-change attribution.',
                         'No fresh retrieval or corrected DMR evidence-recall measurement.']}
    (after/'reader_comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (after/'reader_changes.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in changes), encoding='utf-8')
    report = ['# Reader comparison, 27 October 2026', '',
              f'The same {len(old)} paired questions and archived rankings were replayed with the same Qwen2.5-1.5B Q4_K_M reader, greedy decoding, seed, 48-token output cap, and scoring. Before: top 5, 768 evidence tokens, legacy prompt. After: top 10, 1,800 evidence tokens, concise prompt. This compares the fixed bundle and does not attribute individual changes.', '',
              '| Dataset | Retrieval | n | EM before (%) | EM after (%) | Change (pp) | F1 before (%) | F1 after (%) |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        label = 'Hybrid + reranking' if row['condition'] == 'ironweb' else 'Vector'
        report.append(f"| {LABELS[row['benchmark']]} | {label} | {row['n']} | {row['old_em_percent']:.2f} | {row['new_em_percent']:.2f} | {row['em_delta_pp']:+.2f} | {row['old_f1_percent']:.2f} | {row['new_f1_percent']:.2f} |")
    report.extend(['', '## Descriptive totals', ''])
    for row in totals:
        report.append(f"- {row['condition']}: {row['old_correct']}/{row['n']} to {row['new_correct']}/{row['n']} exact matches ({row['em_delta_pp']:+.2f} pp); token F1 {row['old_f1_percent']:.2f}% to {row['new_f1_percent']:.2f}%.")
    report.extend(['', '## Paired outcome changes', '',
                   '| Dataset | Condition | New wins | New losses | Exact p | Holm p (six tests) |',
                   '|---|---|---:|---:|---:|---:|'])
    for row in rows:
        report.append(f"| {LABELS[row['benchmark']]} | {row['condition']} | {row['wins']} | {row['losses']} | {row['p_exact']:.4f} | {row['p_holm_six_comparisons']:.4f} |")
    report.extend(['', 'Tests describe question-level discordance. Shared histories limit independence; these results do not establish statistical significance across independent conversations. All generation failures remain in the denominator.', '',
                   'This is a reader-only replay of historical retrieval. It does not measure a current-engine retrieval gain. DMR gold evidence still needs review, and scoped Recall@5 would be trivial for its five-session histories. Strict exact match and token F1 are not semantic-judge accuracy. No tuning was performed on these outcomes.'])
    (after/'reader_comparison.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, type=Path)
    parser.add_argument('--after', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.before, args.after), indent=2))
