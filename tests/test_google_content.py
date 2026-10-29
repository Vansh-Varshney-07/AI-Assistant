"""Bounded exact-content projections and API scope with mocked HTTP only."""
import base64
import pytest
from wayfinder.platform.google_content import cell_range,project
from tests.test_platform_sources import sources,Response,mock_google


def message(text):return {'id':'abc','raw':base64.urlsafe_b64encode(text).decode().rstrip('=')}

def test_mime_parser_keeps_plain_text_and_never_treats_html_as_text():
    raw=message(b'Subject: Synthetic\r\nFrom: example@example.test\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nA bounded test message.')
    result=project('gmail_message',raw,'abc')[0]
    assert result['text']=='A bounded test message.' and result['coverage']=='plain_text_parts_only'
    html=project('gmail_message',message(b'Content-Type: text/html\r\n\r\n<script>bad()</script>'),'abc')[0]
    assert html['text']=='' and html['html_only'] and 'text/html' in html['omitted_parts']
    with pytest.raises(ValueError):project('gmail_message',raw,'def')

@pytest.mark.parametrize('value',['Sheet1!A1:XFD1000','Sheet1!A5:B1','A1:B3','https://example.com','Sheet1!A1:ZZ9999'])
def test_range_escape_and_oversized_rectangles_refused(value):
    with pytest.raises(ValueError):cell_range(value)


def test_exact_sheet_response_and_document_coverage_are_checked():
    data={'range':"'Sheet 1'!A1:B2",'values':[['A','B'],['C']]}
    assert project('sheets_values',data,'sheet','Sheet 1!A1:B2')[0]['values'][0]==['A','B']
    with pytest.raises(ValueError):project('sheets_values',data,'sheet','Other!A1:B2')
    with pytest.raises(ValueError):project('sheets_values',{**data,'values':[[1,2,3]]},'sheet','Sheet 1!A1:B2')
    doc={'documentId':'one','title':'Test','body':{'content':[{'paragraph':{'elements':[{'textRun':{'content':'selected'}}]}},{'table':{'private':'not projected'}}]}}
    result=project('docs_text',doc,'one')[0]
    assert result['text']=='selected' and result['coverage']=='first_tab_paragraph_text_only' and 'tables' in result['excluded']


def test_api_selected_message_uses_only_exact_fixed_endpoint(sources):
    _,client,args,_=sources;_,calls=mock_google(sources,Response(message(b'Subject: Test\r\n\r\nHello')))
    grant=client.call('platform_google_grant',**args,service='gmail_message',resource='abc',limit=1)
    result=client.call('platform_google_read',**args,grant=grant['id'])
    assert calls[0][0]=='https://gmail.googleapis.com/gmail/v1/users/me/messages/abc'
    assert calls[0][1]['params']['format']=='raw' and result['records'][0]['text']=='Hello'
    with pytest.raises(ValueError):client.call('platform_google_read',**dict(args,task='other'),grant=grant['id'])
    client.call('platform_google_revoke',**args,grant=grant['id'])
    with pytest.raises(ValueError):client.call('platform_google_read',**args,grant=grant['id'])


def test_exact_content_grants_refuse_unbounded_or_unrelated_fields(sources):
    _,client,args,_=sources;_,calls=mock_google(sources,Response({}))
    for fields in [dict(service='gmail_message',resource='abc',limit=3),dict(service='tasks',resource='list',limit=1,range='Sheet1!A1:B2'),dict(service='sheets_values',resource='sheet',limit=1,range='Sheet1!A1:ZZ999')]:
        with pytest.raises(ValueError):client.call('platform_google_grant',**args,**fields)
    assert not calls
