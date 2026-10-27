"""Text-only benchmark inputs. Gold answers/labels never enter document text.

This is a dataset adapter, not an answer generator or an official scorer.
LoCoMo category 5 remains separate; LongMemEval oracle is not a full-history test.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator
import ijson

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/benchmarks'


@dataclass(frozen=True)
class Document:
    id: str
    session_id: str
    text: str
    date: str


@dataclass(frozen=True)
class Case:
    id: str
    group_id: str
    question: str
    question_date: str
    documents: tuple[Document, ...]
    gold_answer: Any
    gold_evidence: tuple[str, ...]
    category: str
    evidence_unit: str


def dmr_cases(path: Path, evidence_path: Path | None = None) -> Iterator[Case]:
    """Adapt raw MSC/DMR histories without manufacturing evidence labels.

    The source's self_instruct A/B fields contain an answer and question, but
    no evidence-session annotation. Optional reviewed annotations are bound to
    the exact source file hash and use full document IDs, never loop indices.
    """
    annotations = {}
    if evidence_path is not None:
        manifest = json.loads(evidence_path.read_text(encoding='utf-8'))
        with path.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        if manifest.get('source_sha256') != digest:
            raise ValueError('DMR evidence annotations belong to a different source.')
        annotations = manifest['annotations']
    seen = set()
    with path.open(encoding='utf-8') as handle:
        for index, line in enumerate(line for line in handle if line.strip()):
            sample = json.loads(line)
            group = f'dmr:{index:04d}'
            pair = sample.get('self_instruct', {})
            if not pair.get('B') or not pair.get('A'):
                continue
            identifier = group + ':qa'
            seen.add(identifier)
            sessions = sample.get('previous_dialogs', []) + [{'dialog': sample['dialog']}]
            docs = tuple(Document(
                f'{group}:session:{session_index}', f'{group}:session:{session_index}',
                '\n'.join(f"{turn.get('id', 'speaker')}: {turn['text']}"
                          for turn in session['dialog']), '')
                for session_index, session in enumerate(sessions))
            evidence = ()
            if identifier in annotations:
                annotation = annotations[identifier]
                ids = annotation.get('document_ids')
                if (not annotation.get('reviewer') or not annotation.get('rationale')
                        or not isinstance(ids, list) or not ids
                        or any(not isinstance(x, str) for x in ids)
                        or len(ids) != len(set(ids))
                        or set(ids) - {d.id for d in docs}):
                    raise ValueError(f'Invalid reviewed DMR evidence: {identifier}')
                evidence = tuple(ids)
            yield Case(identifier, group, pair['B'], '', docs, pair['A'],
                       evidence, 'msc_dialogue', 'session')
    if set(annotations) - seen:
        raise ValueError('DMR annotations reference unknown question IDs.')


def search_case(engine, case: Case, memory_ids: dict[str, str], *, mode: str, k: int = 10):
    """Apply the same question-local corpus scope to every retrieval condition.

    memory_ids maps source document IDs to the IDs returned by engine.add().
    Never derive the scope from gold evidence or filter only after top-k.
    """
    scope = [memory_ids[d.id] for d in case.documents]
    if not scope or len(set(scope)) != len(scope):
        raise ValueError('Case history must map to distinct ingested memories.')
    hits = engine.search(case.question, k=k, retrieval_mode=mode, document_ids=scope)
    allowed = set(scope)
    if any(hit.memory_id not in allowed for hit in hits):
        raise ValueError('Retriever returned a memory outside the question history.')
    return hits


def locomo_cases(path: Path | None = None) -> Iterator[Case]:
    path = path or BASE / 'sources/locomo/data/locomo10.json'
    with path.open(encoding='utf-8') as handle:
        conversations = json.load(handle)
    for index, sample in enumerate(conversations):
        group = str(sample.get('sample_id', index))
        conv = sample['conversation']
        documents = []
        for key, turns in conv.items():
            if not key.startswith('session_') or not isinstance(turns, list):
                continue
            date = str(conv.get(key + '_date_time', ''))
            for turn in turns:
                # Do not ingest QA, event summaries, observations, or evidence labels.
                text = f"Date: {date}\n{turn['speaker']}: {turn['text']}"
                documents.append(Document(str(turn['dia_id']), key, text, date))
        docs = tuple(documents)
        for qindex, qa in enumerate(sample['qa']):
            yield Case(f'{group}:q{qindex}', group, qa['question'], '', docs,
                       qa.get('answer'), tuple(map(str, qa.get('evidence', []))),
                       str(qa['category']), 'dialogue_turn')


def longmemeval_cases(variant: str = 's', path: Path | None = None) -> Iterator[Case]:
    names = {'s': 'longmemeval_s_cleaned.json', 'm': 'longmemeval_m_cleaned.json',
             'oracle': 'longmemeval_oracle.json'}
    if variant not in names:
        raise ValueError('Choose s, m, or oracle explicitly.')
    path = path or BASE / 'datasets/longmemeval' / names[variant]
    with path.open('rb') as handle:
        for sample in ijson.items(handle, 'item', use_float=True):
            ids, sessions, dates = (sample['haystack_session_ids'],
                                    sample['haystack_sessions'], sample['haystack_dates'])
            if not len(ids) == len(sessions) == len(dates):
                raise ValueError('Session identifiers, dates and histories are misaligned.')
            docs = []
            for session_index, (session_id, turns, date) in enumerate(zip(ids, sessions, dates)):
                for index, turn in enumerate(turns):
                    # Deliberately ignore any `has_answer` annotation on a turn.
                    text = f"Date: {date}\n{turn['role']}: {turn['content']}"
                    # Some source histories repeat a session ID. Preserve every
                    # occurrence, while keeping the original session ID for scoring.
                    docs.append(Document(f'session{session_index}:{session_id}:turn{index}', str(session_id),
                                         text, str(date)))
            qid = str(sample['question_id'])
            yield Case(qid, qid, sample['question'], str(sample['question_date']),
                       tuple(docs), sample['answer'],
                       tuple(map(str, sample['answer_session_ids'])),
                       sample['question_type'], 'session')
