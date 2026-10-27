"""Synthetic contract tests. Real model qualification is a separate packaged check."""
import time
from threading import Event
import pytest
from tests.test_wayfinder_app import app,space,call

PIN=dict(model='fixture-model',provider='custom',endpoint='inference.local')
class Model:
    def __init__(self):self.payloads=[];self.release=Event();self.release.set()
    def run(self,payload,cancelled):
        self.payloads.append(payload)
        while not self.release.wait(.01):
            if cancelled.is_set():raise ValueError('stopped')
        return dict(ok=True,effective_tools=[],text='Synthetic reply')

@pytest.fixture
def chat_app(app):
    sid=space(app,'Synthetic chat');model=Model();app.workers.bridge=model;app.chat.approved_model=PIN
    app.platform.inspector.snapshot=dict(compatible=True,isolation=dict(model_info=PIN),fingerprint='fixture',expires=time.time()+300)
    cid=call(app,'chat_new',space=sid)['id']
    return app,sid,cid,model

def terminal(app,sid,cid):
    for _ in range(100):
        result=call(app,'chat_get',space=sid,conversation=cid)
        if result['turns'] and result['turns'][-1]['status'] not in {'reserved','running'}:return result
        time.sleep(.01)
    pytest.fail('Synthetic worker did not terminate')

def send(app,sid,cid,request='r1',message='Hello'):
    return call(app,'chat_send',space=sid,conversation=cid,request_id=request,message=message)

def test_real_hub_history_dedup_and_memory_separation(chat_app):
    app,sid,cid,model=chat_app
    send(app,sid,cid);first=terminal(app,sid,cid)
    assert first['turns'][0]['assistant_text']=='Synthetic reply'
    send(app,sid,cid);assert len(model.payloads)==1
    with pytest.raises(ValueError,match='immutable'):send(app,sid,cid,message='Changed')
    send(app,sid,cid,'r2','Continue');second=terminal(app,sid,cid)
    assert model.payloads[1]['history']==[dict(role='user',content='Hello'),dict(role='assistant',content='Synthetic reply')]
    assert model.payloads[1]['model_pin']==PIN and second['memory_automatic'] is False
    with app.db() as db:assert db.execute('SELECT count(*) FROM memory_actions').fetchone()[0]==0

def test_scope_unknown_fields_and_unapproved_provider(chat_app):
    app,sid,cid,model=chat_app
    other=space(app,'Other')
    with pytest.raises(ValueError,match='unavailable'):call(app,'chat_get',space=other,conversation=cid)
    with pytest.raises(ValueError,match='fields'):call(app,'chat_send',space=sid,conversation=cid,request_id='x',message='hi',history=[])
    app.chat.approved_model={**PIN,'model':'changed'}
    with pytest.raises(ValueError,match='model connection'):send(app,sid,cid)
    assert not model.payloads

def test_cancel_and_no_implicit_retry(chat_app):
    app,sid,cid,model=chat_app;model.release.clear()
    state=send(app,sid,cid);turn=state['turns'][0]['id']
    with pytest.raises(ValueError,match='already generating'):send(app,sid,cid,'another')
    cancelled=call(app,'chat_cancel',space=sid,conversation=cid,turn=turn)
    assert cancelled['turns'][0]['status']=='cancelled'
    model.release.set();time.sleep(.05)
    assert terminal(app,sid,cid)['turns'][0]['status']=='cancelled'
    send(app,sid,cid,'after','new');terminal(app,sid,cid)
    assert model.payloads[-1]['history']==[]

def test_bounded_history_and_delete(chat_app):
    app,sid,cid,model=chat_app
    for i in range(8):send(app,sid,cid,str(i),str(i));terminal(app,sid,cid)
    assert len(model.payloads[-1]['history'])==12
    page=call(app,'chat_get',space=sid,conversation=cid);assert len(page['turns'])==6 and page['has_more']
    older=call(app,'chat_get',space=sid,conversation=cid,before=page['before']);assert len(older['turns'])==2
    assert call(app,'chat_delete',space=sid,conversation=cid)['memory_changed'] is False
    assert call(app,'chat_list',space=sid)==[]

def test_recovery_marks_reserved_without_replay(chat_app):
    from wayfinder.chat import ChatService
    app,sid,cid,model=chat_app
    with app.db() as db:db.execute("INSERT INTO chat_turns VALUES ('orphan',?,'lost','digest','hello',NULL,'reserved',NULL,?,0,NULL)",(cid,time.time()))
    restored=ChatService(app)
    with app.db() as db:assert db.execute("SELECT status FROM chat_turns WHERE id='orphan'").fetchone()[0]=='interrupted'
    assert not model.payloads
