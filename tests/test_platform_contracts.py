"""Platform wrappers do not change worker schemas or grant resource authority."""
import pytest
from pydantic import ValidationError
from wayfinder.platform.contracts import ArtifactReference,Scope,TaskEnvelope,WorkerOutcome
from wayfinder.platform.catalog import CapabilityCatalog,FILE_ANALYST
from types import SimpleNamespace

def request():
    return TaskEnvelope(request_id='client-request',run_id='a'*32,worker_role='W35',scope=Scope(owner='owner',space='space',task='selected-task'),deadline=12345.0,cancellation_id='cancel-ref',artifacts=(ArtifactReference(reference='opaque',sha256='b'*64,media_type='text/plain'),))

def test_transport_round_trip_and_no_authority_fields():
    item=request()
    assert TaskEnvelope.model_validate_json(item.model_dump_json())==item
    assert item.scope.worker_scope()==('owner','space','selected-task')
    for changes in ({'approved':True},{'tools':['terminal']},{'worker_role':'W48'},{'worker_role':'W00'},{'deadline':float('inf')},{'contract':'wayfinder.task-envelope/2'}):
        with pytest.raises(ValidationError):TaskEnvelope.model_validate({**item.model_dump(),**changes})
    with pytest.raises(ValidationError):item.scope.task='other'

def test_outcome_requires_real_bounded_finite_output():
    fields=dict(run_id='a'*32,status='completed',execution_ref='job-ref')
    for output in (None,{'value':float('nan')},{'long':'x'*33000},{'object':object()}):
        with pytest.raises(ValidationError):WorkerOutcome(**fields,output=output)
    outcome=WorkerOutcome(**fields,output={'text':'Bounded result'},evidence=request().artifacts)
    assert WorkerOutcome.model_validate_json(outcome.model_dump_json())==outcome

def test_capability_projection_never_converts_metadata_into_permission():
    state={'compatible':True}
    inspector=SimpleNamespace(current=lambda:state)
    candidates=[SimpleNamespace(id=tool,name=tool,score=1,status='catalogued') for tool in [FILE_ANALYST,'arbitrary.terminal']]
    catalog=CapabilityCatalog(inspector,lambda *args,**kwargs:candidates)
    file,terminal=catalog.search('selected file')
    assert file['available'] and file['qualified'] and file['required_permissions']
    assert not file['executable'] and not terminal['available'] and not terminal['configured']
    state['compatible']=False
    assert not catalog.search('selected file')[0]['available']
    with pytest.raises(ValueError):catalog.select_read_only('selected file')
