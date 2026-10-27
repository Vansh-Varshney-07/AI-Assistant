"""Versioned task focus over existing handlers; no agent loop or tool delegation runtime."""
import hashlib
import json
from pathlib import Path
from threading import RLock
import time
import uuid
from pydantic import BaseModel, ConfigDict, Field, ValidationError

SCHEMAS = {
    'platform_profiles': set(), 'platform_profile_start': {'request'},
    'platform_profile_result': {'id'}, 'platform_profile_cancel': {'id'},
    'platform_profile_runs': set(), 'platform_profile_clear': {'id'},
}
TERMINAL = {'completed','failed','stale','cancelled','interrupted'}
FILE_BINDINGS = frozenset({'A01','A05','A06'})
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

class TaskRequest(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    request_id: str = Field(min_length=1,max_length=100)
    profile_id: str = Field(min_length=3,max_length=3)
    profile_version: str = '1'
    preset_id: str | None = None
    reference: str = Field(min_length=1,max_length=200)
    goal: str = Field(min_length=1,max_length=1000)

class TaskProfiles:
    def __init__(self,platform):
        self.platform,self.app,self.lock = platform,platform.app,RLock()
        raw=Path(__file__).with_name('task-profiles.json').read_bytes()
        self.manifest=json.loads(raw)
        if self.manifest.get('contract')!='wayfinder.task-profiles/1':raise ValueError('Unsupported task-profile manifest.')
        self.manifest_hash=hashlib.sha256(raw).hexdigest()
        with self.app.db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS task_profile_runs(
                id TEXT PRIMARY KEY,scope TEXT,request TEXT,digest TEXT,body TEXT,profile TEXT,
                manifest TEXT,source TEXT,job TEXT,status TEXT,created REAL,
                UNIQUE(scope,request))''')
            db.execute("UPDATE task_profile_runs SET status='interrupted' WHERE status IN ('reserved','running')")

    def catalog(self):
        qualified=bool(self.platform.inspector.current().get('compatible'))
        profiles=[]
        for item in self.manifest['profiles']:
            file_binding=item['id'] in FILE_BINDINGS
            profiles.append(dict(item,execution=dict(
                available=file_binding and qualified,
                included=file_binding,
                mode='selected_file' if file_binding else 'existing_memory_view' if item['id']=='A07' else None,
                status='ready_for_selected_file' if file_binding and qualified else 'runtime_inspection_required' if file_binding else 'existing_memory_view' if item['id']=='A07' else 'deferred' if item['id']=='A08' else 'connection_or_adapter_unqualified',
                binding='existing.W35' if file_binding else None,
                note='Selected UTF-8 file only. No live retrieval, provider access, effects, or helpers.' if file_binding else item['limitation'])))
        return dict(contract=self.manifest['contract'],version=self.manifest['version'],manifest_sha256=self.manifest_hash,
                    main=self.manifest['main'],profiles=profiles,presets=[dict(p,available=False,status='provider_operations_unqualified') for p in self.manifest['presets']],
                    limits=dict(max_active_existing_workers=2,max_worker_invocations=1,delegation_depth=0,deadline_seconds=110,cost=None,tokens=None))

    def call(self,who,scope,operation,body):
        self.app.authorize(who);self.app.space(who,scope.space)
        if who.owner!=scope.owner or operation not in SCHEMAS or set(body)-({'space','task'}|SCHEMAS[operation]):raise ValueError('Invalid task-profile scope or fields.')
        with self.lock:
            if self.app.closed or self.platform.closed:raise ValueError('Task routing is stopped.')
            if operation=='platform_profiles':return self.catalog()
            if operation=='platform_profile_start':
                try:request=TaskRequest.model_validate(body.get('request'))
                except ValidationError:raise ValueError('Invalid task-profile request fields or limits.') from None
                return self.start(scope,request)
            if operation=='platform_profile_runs':
                with self.app.db() as db:rows=db.execute('SELECT id FROM task_profile_runs WHERE scope=? ORDER BY created DESC LIMIT 8',(canonical(scope.worker_scope()),)).fetchall()
                return [dict(self.result(scope,row['id']),result=None) for row in rows]
            row=self.row(scope,body.get('id'))
            if operation=='platform_profile_cancel':
                if row['status'] not in TERMINAL:
                    self.update(row['id'],status='cancelled')
                    if row['job']:self.app.workers.cancel(scope.worker_scope(),row['job'])
                return self.result(scope,row['id'])
            if operation=='platform_profile_clear':
                if row['status'] not in TERMINAL:raise ValueError('Stop this task before clearing its artifact.')
                if row['job']:self.app.workers.forget(scope.worker_scope(),row['job'])
                with self.app.db() as db:db.execute('DELETE FROM task_profile_runs WHERE id=?',(row['id'],))
                return dict(cleared=True,scope='This task and its separate worker artifact only; no memory or backups erased.')
            return self.result(scope,row['id'])

    def row(self,scope,rid):
        if not isinstance(rid,str) or not 1<=len(rid)<=100:raise ValueError('Choose one bounded task ID.')
        with self.app.db() as db:row=db.execute('SELECT * FROM task_profile_runs WHERE id=? AND scope=?',(rid,canonical(scope.worker_scope()))).fetchone()
        if not row:raise ValueError('Task unavailable in this scope.')
        return dict(row)

    def update(self,rid,*,status,job=None):
        with self.app.db() as db:
            if job is None:db.execute('UPDATE task_profile_runs SET status=? WHERE id=?',(status,rid))
            else:db.execute('UPDATE task_profile_runs SET status=?,job=? WHERE id=?',(status,job,rid))

    def start(self,scope,request):
        body=request.model_dump();digest=hashlib.sha256(canonical(body).encode()).hexdigest()
        with self.app.db() as db:old=db.execute('SELECT id,digest FROM task_profile_runs WHERE scope=? AND request=?',(canonical(scope.worker_scope()),request.request_id)).fetchone()
        if old:
            if old['digest']!=digest:raise ValueError('Task request ID belongs to different immutable input.')
            return self.result(scope,old['id'])
        if request.preset_id is not None:raise ValueError('App presets are defined but provider operations are not qualified. No fallback task was dispatched.')
        if request.profile_id not in FILE_BINDINGS or request.profile_version!='1':raise ValueError('This profile/version has no qualified execution adapter.')
        if not request.goal.strip() or len(request.goal.encode('utf-8'))>1000:raise ValueError('Enter a nonblank goal within the bounded text limit (1,000 UTF-8 bytes).')
        self.platform.inspector.require()
        source=self.app.workers.files.read(scope.worker_scope(),request.reference)
        if source['extension'] not in {'.txt','.md','.csv','.json','.log'}:raise ValueError('Task profiles currently accept selected UTF-8 text files only.')
        # This reuses FileBroker identity/hash checks, and never transfers a grant to another task.
        source_ref=dict(reference=request.reference,name=source['name'],sha256=source['sha256'])
        rid=uuid.uuid4().hex
        with self.app.db() as db:db.execute("INSERT INTO task_profile_runs VALUES (?,?,?,?,?,?,?,?,NULL,'reserved',?)",(rid,canonical(scope.worker_scope()),request.request_id,digest,canonical(body),request.profile_id,self.manifest_hash,canonical(source_ref),time.time()))
        try:
            # One existing isolated worker is the entire qualified lead path. No nested model loop.
            job=self.app.workers.start(scope.worker_scope(),role='W35',question=request.goal,reference=request.reference)
            self.update(rid,status='running',job=job['id'])
        except Exception:
            self.update(rid,status='failed')
            raise ValueError('The bounded selected-file task could not start. No automatic retry was made.') from None
        return self.result(scope,rid)

    def result(self,scope,rid):
        row=self.row(scope,rid);result=None;warning=None
        job=None
        if row['job']:
            try:job=self.app.workers.get(scope.worker_scope(),row['job'])
            except ValueError:warning='The underlying worker artifact is unavailable.'
        if row['status']=='running' and job:
            if job['status']=='completed':
                try:
                    selected=self.app.workers.files.read(scope.worker_scope(),json.loads(row['body'])['reference'])
                    expected=json.loads(row['source'])['sha256']
                    if selected['sha256']!=expected or job['result'].get('evidence',{}).get('sha256')!=expected:raise ValueError('Source changed')
                    self.update(rid,status='completed')
                except ValueError:self.update(rid,status='stale')
            elif job['status'] in {'failed','stopped','interrupted'}:self.update(rid,status='cancelled' if job['status']=='stopped' else job['status'])
            row=self.row(scope,rid)
        if row['status']=='completed' and job and job['status']=='completed':
            result=dict(text=job['result']['text'],sources=[dict(json.loads(row['source']),truncated=job['result'].get('evidence',{}).get('truncated',False))],historical_artifact=True)
        return dict(id=row['id'],profile_id=row['profile'],profile_version='1',manifest_sha256=row['manifest'],status=row['status'],created=row['created'],goal=json.loads(row['body'])['goal'],job=row['job'],binding='existing.W35',result=result,warning=warning or ('Upstream abort/billing is unconfirmed; no automatic replay.' if row['status'] in {'cancelled','interrupted'} else None),metrics=dict(worker_invocations=1 if row['job'] else 0,delegations=0,tokens=None,cost=None),effects_executed=False)
