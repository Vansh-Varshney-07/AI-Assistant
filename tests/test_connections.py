"""Synthetic contracts and isolated app SQLite; no live account content."""
from threading import Event,Thread
import json,time
import pytest
from wayfinder.service import AppService,Identity
from wayfinder.api import Client,serve
from wayfinder.atlas.harness.base import KnowledgeItem

PAGE='01234567-1234-1234-1234-0123456789ab'
class NoMemory:
    def close(self):pass
class FakeNotion:
    possibly_truncated=False
    def __init__(self,key):self.key=key
    def search(self,query,limit=3):return [KnowledgeItem(id=PAGE,title='Synthetic page',content='',provider='notion',url='https://notion.so/'+PAGE)]
    def read(self,item):return KnowledgeItem(id=item,title='Synthetic page',content='Only synthetic content.',provider='notion',url='https://notion.so/'+item)
    def _request(self,endpoint):return {'type':'bot'}
class FakeSearch:
    def __init__(self):self.calls=[]
    def run(self,payload,cancelled):self.calls.append(payload);return {'ok':True,'effective_tools':[],'data':{'web':[{'title':'Synthetic source','url':'https://example.com','description':'Synthetic web evidence'}]}}
@pytest.fixture
def linked(tmp_path):
    app=AppService(tmp_path/'runtime',NoMemory());app.platform.connections.notion_factory=FakeNotion;search=FakeSearch();app.platform.connections.bridge=search
    app.platform.connections.configure({'schema':1,'google':None,'tavily':'PRIVATE_SEARCH_KEY','notion':'PRIVATE_NOTION_KEY'})
    server=serve(app);client=Client(server.server_port,app.token);sid=client.call('create_space',name='Connection test')['id'];args={'space':sid,'task':'read-test'}
    yield app,client,args,search
    server.shutdown();server.server_close();app.close()
def test_private_configuration_is_not_an_api_capability(linked):
    app,client,args,_=linked
    with pytest.raises(ValueError):client.call('connections_configure',connections={'schema':1})
    with pytest.raises(ValueError):client.call('platform_connections_status',**args,api_key='forged')
    with pytest.raises(ValueError):app.call(Identity(app.owner,'worker'),'platform_external_grant',{**args,'provider':'notion','intent':'search','query':'test'})
def test_status_and_live_reads_do_not_return_or_store_credentials(linked):
    app,client,args,search=linked
    status=client.call('platform_connections_status',**args);assert status['configured']=={'google':False,'notion':True,'tavily':True}
    grant=client.call('platform_external_grant',**args,provider='tavily',intent='search',query='synthetic query')
    result=client.call('platform_external_read',**args,grant=grant['id']);assert result['records'][0]['title']=='Synthetic source' and result['model_invocations']==0
    assert search.calls[0]['role']=='TAVILY' and search.calls[0]['limit']==3
    with app.db() as db:dump='\n'.join(db.iterdump());row=db.execute('SELECT status,records FROM integration_reads').fetchone()
    assert row['status']=='completed' and row['records']==1
    for secret in ['PRIVATE_SEARCH_KEY','PRIVATE_NOTION_KEY','synthetic query']:
        assert secret not in json.dumps(status) and secret not in json.dumps(result) and secret not in dump
def test_task_space_revocation_expiry_and_changed_credentials(linked):
    app,client,args,_=linked
    grant=client.call('platform_external_grant',**args,provider='notion',intent='read',item=PAGE)
    other=client.call('create_space',name='Other')['id']
    for changed in [{**args,'task':'other'},{**args,'space':other}]:
        with pytest.raises(ValueError):client.call('platform_external_read',**changed,grant=grant['id'])
    client.call('platform_external_revoke',**args,grant=grant['id'])
    with pytest.raises(ValueError):client.call('platform_external_read',**args,grant=grant['id'])
    grant=client.call('platform_external_grant',**args,provider='notion',intent='read',item=PAGE)
    app.platform.connections.grants[grant['id']]['expires']=time.time()-1
    with pytest.raises(ValueError):client.call('platform_external_read',**args,grant=grant['id'])
    grant=client.call('platform_external_grant',**args,provider='notion',intent='read',item=PAGE)
    app.platform.connections.configure({'schema':1,'google':None,'tavily':None,'notion':'ROTATED_PRIVATE_KEY'})
    with pytest.raises(ValueError):client.call('platform_external_read',**args,grant=grant['id'])
def test_rotation_during_read_prevents_late_result_publication(linked):
    app,client,args,_=linked;entered,release=Event(),Event()
    class Slow(FakeNotion):
        def read(self,item):entered.set();release.wait(5);return super().read(item)
    app.platform.connections.notion_factory=Slow
    grant=client.call('platform_external_grant',**args,provider='notion',intent='read',item=PAGE);errors=[]
    def read():
        try:client.call('platform_external_read',**args,grant=grant['id'])
        except ValueError as error:errors.append(str(error))
    thread=Thread(target=read);thread.start();assert entered.wait(2)
    app.platform.connections.configure({'schema':1,'google':None,'tavily':None,'notion':None});release.set();thread.join(5)
    assert errors and 'changed' in errors[0]
    with app.db() as db:assert db.execute('SELECT status FROM integration_reads').fetchone()[0]=='failed'
def test_no_write_intents_arbitrary_urls_or_unbounded_queries(linked):
    _,client,args,_=linked
    for body in [{'provider':'notion','intent':'create','item':PAGE},{'provider':'notion','intent':'read','item':'https://example.com/private'},{'provider':'tavily','intent':'search','query':'x'*401},{'provider':'tavily','intent':'search','query':'x','url':'https://attacker.invalid'}]:
        with pytest.raises(ValueError):client.call('platform_external_grant',**args,**body)
def test_notion_source_adapter_is_reused_with_a_read_only_transport():
    from wayfinder.platform.connections import BoundedNotion
    from wayfinder.atlas.harness.notion_adapter import NotionAdapter
    assert issubclass(BoundedNotion,NotionAdapter)
    with pytest.raises(ValueError,match='bounded reads'):BoundedNotion('fixture')._request('pages',method='POST',data={'title':'forbidden'})

def test_provider_value_errors_cannot_echo_private_content(linked):
    app,client,args,_=linked
    class Broken(FakeNotion):
        def search(self,*a,**k):raise ValueError('PRIVATE_PROVIDER_CONTENT')
    app.platform.connections.notion_factory=Broken
    grant=client.call('platform_external_grant',**args,provider='notion',intent='search',query='')
    with pytest.raises(ValueError) as error:client.call('platform_external_read',**args,grant=grant['id'])
    assert 'PRIVATE_PROVIDER_CONTENT' not in str(error.value)
