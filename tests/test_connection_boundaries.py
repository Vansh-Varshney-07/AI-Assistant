"""Synthetic provider-boundary qualification, never live accounts."""
import json,runpy,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from tests.test_platform_sources import sources,Response,Session,mock_google

@pytest.mark.parametrize('service,resource,payload,field',[
    ('drive','folder1',{'files':[{'id':'one','name':'Synthetic','private':'forbidden'}]},'name'),
    ('docs','one',{'documentId':'one','title':'Synthetic','body':'forbidden'},'title'),
    ('sheets','one',{'spreadsheetId':'one','properties':{'title':'Synthetic'},'sheets':[],'values':'forbidden'},'title'),
    ('contacts','me',{'connections':[{'resourceName':'people/one','names':[{'displayName':'Synthetic'}],'emailAddresses':[],'private':'forbidden'}]},'name'),
])
def test_google_added_sources_strip_fields_and_obey_exact_grants(sources,service,resource,payload,field):
    _,client,args,_=sources;_,calls=mock_google(sources,Response(payload))
    grant=client.call('platform_google_grant',**args,service=service,resource=resource,limit=1)
    result=client.call('platform_google_read',**args,grant=grant['id'])
    assert result['records'][0][field]=='Synthetic' and 'forbidden' not in json.dumps(result)
    assert calls[0][1]['allow_redirects'] is False
    if service=='drive':assert "'folder1' in parents" in calls[0][1]['params']['q']
    if service in {'docs','sheets'}:assert result['records'][0]['metadata_only']

def test_gmail_metadata_cannot_return_a_different_message(sources):
    app,client,args,_=sources;calls=[]
    class Ordered(Session):
        def get(self,url,**kwargs):
            calls.append(url)
            return Response({'messages':[{'id':'one'}]} if len(calls)==1 else {'id':'different','snippet':'forbidden'})
    app.platform.google.session_factory=lambda service:Ordered(None,calls)
    grant=client.call('platform_google_grant',**args,service='gmail_headers',resource='INBOX',limit=1)
    with pytest.raises(ValueError,match='different message'):client.call('platform_google_read',**args,grant=grant['id'])

@pytest.mark.parametrize('model,endpoint,role',[
    ('gemini-3.5-flash-lite','https://integrate.api.nvidia.com/v1','probe'),
    ('nvidia/nemotron-3.5-lightning-30b-a3b','https://inference.local/v1','probe'),
    ('nvidia/nemotron-3-ultra-550b-a55b','https://integrate.api.nvidia.com/v1','W33'),
])
def test_runner_rejects_other_models_endpoints_and_automatic_vision(monkeypatch,model,endpoint,role):
    runner=runpy.run_path(str(Path(__file__).parents[1]/'wayfinder/workers/hermes_runner.py'),run_name='qualified_runner')
    route=dict(model=model,base_url=endpoint,api_key='SYNTHETIC',provider='custom')
    monkeypatch.setattr(subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout='WAYFINDER_ROUTE='+json.dumps(route)))
    with pytest.raises(ValueError,match='Only NVIDIA|Image analysis'):runner['main']({'role':role})
