"""Task-profile contract/failure tier; fixture model and disposable actual storage."""
from concurrent.futures import ThreadPoolExecutor
import time
import pytest
from tests.test_platform_integration import platform
from wayfinder.platform.task_profiles import TaskProfiles
from wayfinder.service import Identity

def call(f,op,**body):return f['client'].call(op,**f['args'],**body)
def request(f,**fields):return dict(request_id='profile-once',profile_id='A05',profile_version='1',reference=f['request']['reference'],goal='Create a study guide and cite the supplied source.',**fields)
def start(f,**changes):
    r=request(f);r.update(changes)
    return call(f,'platform_profile_start',request=r)
def settle(f,rid):
    end=time.monotonic()+5
    while time.monotonic()<end:
        row=call(f,'platform_profile_result',id=rid)
        if row['status'] not in {'running','reserved'}:return row
        time.sleep(.01)
    raise AssertionError('Task did not settle')

def test_manifest_inventory_does_not_mint_connections(platform):
    c=call(platform,'platform_profiles')
    assert c['main']['id']=='M00' and len(c['profiles'])==8 and len(c['presets'])==6
    assert all(not p['available'] for p in c['presets'])
    assert next(p for p in c['profiles'] if p['id']=='A08')['execution']['status']=='deferred'
    assert next(p for p in c['profiles'] if p['id']=='A05')['execution']['binding']=='existing.W35'
    assert c['limits']['delegation_depth']==0

@pytest.mark.parametrize('profile',['A01','A05','A06'])
def test_existing_file_capability_is_shared_without_another_agent_loop(platform,profile):
    row=start(platform,profile_id=profile)
    result=settle(platform,row['id'])
    assert result['status']=='completed' and result['profile_id']==profile
    assert result['result']['sources'][0]['name']=='selected.md'
    assert result['result']['sources'][0]['sha256']
    assert result['binding']=='existing.W35' and not result['effects_executed']
    assert result['metrics']==dict(worker_invocations=1,delegations=0,tokens=None,cost=None)
    assert len(platform['worker'].payloads)==1 and platform['worker'].payloads[0]['role']=='W35'
    assert call(platform,'platform_profile_runs')[0]['result'] is None

def test_duplicate_request_observes_and_changed_payload_is_rejected(platform):
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(lambda _:start(platform),range(2)))
    assert rows[0]['id']==rows[1]['id']
    assert len(platform['worker'].payloads)==1
    with pytest.raises(ValueError,match='immutable'):start(platform,goal='Changed after acceptance')

def test_direct_baseline_and_profile_use_the_same_worker_payload_without_extra_reasoning(platform):
    goal=request(platform)['goal']
    direct=call(platform,'worker_start',role='W35',reference=platform['request']['reference'],question=goal)
    row=start(platform);settle(platform,row['id'])
    assert len(platform['worker'].payloads)==2
    assert platform['worker'].payloads[0]==platform['worker'].payloads[1]
    assert call(platform,'worker_result',id=direct['id'])['status']=='completed'

@pytest.mark.parametrize('changes',[{'profile_id':'A08'},{'profile_id':'A03'},{'profile_version':'2'},{'preset_id':'P01'},{'tools':['terminal']},{'goal':' '},{'goal':'界'*400}])
def test_unqualified_modes_versions_and_extra_authority_fail_before_dispatch(platform,changes):
    with pytest.raises(ValueError):start(platform,**changes)
    assert platform['worker'].payloads==[]

def test_cross_task_file_grant_and_foreign_owner_are_denied(platform):
    with pytest.raises(ValueError):platform['client'].call('platform_profile_start',space=platform['args']['space'],task='foreign-task',request=request(platform))
    scope=platform['app'].platform._scope(platform['app'].authenticate(platform['app'].token),platform['args'])
    with pytest.raises(ValueError):platform['app'].platform.profiles.call(Identity('foreign','worker'),scope,'platform_profiles',platform['args'])
    assert platform['worker'].payloads==[]

def test_revoked_source_and_cancelled_parent_cannot_publish_a_late_result(platform):
    worker=platform['worker'];worker.release.clear()
    row=start(platform)
    assert worker.entered.wait(2)
    stopped=call(platform,'platform_profile_cancel',id=row['id'])
    assert stopped['status']=='cancelled' and stopped['result'] is None
    worker.release.set()
    assert call(platform,'platform_profile_result',id=row['id'])['result'] is None
    assert 'unconfirmed' in stopped['warning']

def test_revoked_file_fails_without_a_model_artifact(platform):
    platform['worker'].release.clear();row=start(platform)
    assert platform['worker'].entered.wait(2)
    call(platform,'worker_revoke',grant=platform['grant']['id'])
    platform['worker'].release.set()
    outcome=settle(platform,row['id'])
    assert outcome['status'] in {'failed','stale','cancelled'} and outcome['result'] is None

def test_service_restart_interrupts_without_replaying_reserved_work(platform):
    platform['worker'].release.clear();row=start(platform)
    platform['app'].platform.profiles=TaskProfiles(platform['app'].platform)
    replay=start(platform)
    assert replay['id']==row['id'] and replay['status']=='interrupted' and replay['result'] is None
    assert len(platform['worker'].payloads)==1

def test_expired_runtime_and_missing_reference_are_not_availability(platform):
    platform['app'].platform.inspector.snapshot['expires']=0
    with pytest.raises(ValueError):start(platform)
    assert not next(p for p in call(platform,'platform_profiles')['profiles'] if p['id']=='A05')['execution']['available']
    assert not platform['worker'].payloads

def test_clearing_task_clears_only_the_linked_worker_artifact(platform):
    row=start(platform);done=settle(platform,row['id'])
    receipt=call(platform,'platform_profile_clear',id=row['id'])
    assert receipt['cleared']
    with pytest.raises(ValueError):call(platform,'platform_profile_result',id=row['id'])
    with pytest.raises(ValueError):platform['app'].workers.get((platform['app'].owner,platform['args']['space'],platform['args']['task']),done['job'])
