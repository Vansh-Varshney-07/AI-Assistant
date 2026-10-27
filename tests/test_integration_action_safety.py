"""Integration regressions: durable family fencing and monotonic approval expiry."""
import pytest
from wayfinder.workers.actions import ActionGate
from tests.test_desktop_workers import FixtureDriver, database, plan, SCOPE
from tests.test_platform_git import connector, propose, approve, call


def test_monotonic_expiry_survives_wall_clock_rollback(tmp_path):
    wall, monotonic = [1000], [10]
    driver = FixtureDriver()
    gate = ActionGate(database(tmp_path/'gate.db'), driver, clock=lambda:wall[0], monotonic=lambda:monotonic[0])
    item = gate.propose(SCOPE, plan())
    wall[0] = 1
    monotonic[0] = 131
    assert gate.decide(SCOPE,item['id'],True)['status']=='expired'
    assert not driver.effects


def test_unknown_family_denies_new_task_and_pending_approval_after_restart(tmp_path):
    connect = database(tmp_path/'gate.db')
    driver = FixtureDriver()
    gate = ActionGate(connect, driver)
    pending = gate.propose(SCOPE, plan())
    lost = gate.propose(SCOPE, plan())
    driver.crash = True
    assert gate.decide(SCOPE,lost['id'],True)['status']=='outcome_unknown'
    with pytest.raises(ValueError,match='unresolved'):
        gate.propose((SCOPE[0],SCOPE[1],'different-task'),plan())
    with pytest.raises(ValueError,match='unresolved'):
        gate.decide(SCOPE,pending['id'],True)
    restarted = ActionGate(connect, driver)
    assert restarted.get(SCOPE,lost['id'])['status']=='outcome_unknown'
    with pytest.raises(ValueError,match='unresolved'):
        restarted.propose((SCOPE[0],SCOPE[1],'after-restart'),plan())
    assert len(driver.effects)==1


def test_real_git_unknown_family_cannot_bypass_with_a_new_task(connector, monkeypatch):
    service=connector['app'].platform.connectors
    original=service.git.perform
    def lost(*args):
        original(*args)
        raise RuntimeError('Synthetic lost acknowledgement')
    monkeypatch.setattr(service.git,'perform',lost)
    item=propose(connector)
    assert approve(connector,item)['status']=='outcome_unknown'
    other=dict(connector,args=dict(connector['args'],task='new-task'))
    grant=call(other,'platform_git_grant',path=str(connector['root']))
    other['grant']=grant
    with pytest.raises(ValueError,match='unresolved'):
        propose(other,request='different-id',branch='refs/heads/codex/no-bypass')
    assert service.git.dispatches==1


def test_real_git_monotonic_deadline_rechecked_at_process_dispatch(connector, monkeypatch):
    service=connector['app'].platform.connectors
    ticks=[10]
    service.actions.monotonic=lambda:ticks[0]
    item=propose(connector)
    original=service.git._run
    def delayed(root,args,**kwargs):
        if args[0]=='update-ref':
            ticks[0]=131
        return original(root,args,**kwargs)
    monkeypatch.setattr(service.git,'_run',delayed)
    assert approve(connector,item)['status']=='outcome_unknown'
    assert service.git.dispatches==0
