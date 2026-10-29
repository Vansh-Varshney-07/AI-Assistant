"""Bounded Google content projections; email MIME parsing reuses Python's stdlib."""
import base64
from email import policy
from email.parser import BytesParser
import re

def cell_range(value):
    if not isinstance(value,str):raise ValueError('Choose an exact bounded sheet range.')
    match=re.fullmatch(r"'?([A-Za-z0-9 _-]{1,50})'?!([A-Z]{1,2})([1-9][0-9]{0,3}):([A-Z]{1,2})([1-9][0-9]{0,3})",value)
    if not match:raise ValueError('Use an exact sheet and rectangular A1 range, for example Sheet1!A1:D20.')
    name,a,r1,b,r2=match.groups()
    def col(s):
        n=0
        for c in s:n=n*26+ord(c)-64
        return n
    width,height=col(b)-col(a)+1,int(r2)-int(r1)+1
    if width<1 or height<1 or width*height>200:raise ValueError('A sheet read is limited to 200 cells.')
    return dict(normalized=f'{name}!{a}{r1}:{b}{r2}',width=width,height=height)

def project(service,data,resource,selected_range=None):
    if service=='gmail_message':
        if data.get('id')!=resource:raise ValueError('Returned message identity differs from the selected message.')
        raw=data.get('raw')
        if not isinstance(raw,str) or len(raw)>88000:raise ValueError('Message exceeds its MIME byte budget.')
        decoded=base64.b64decode(raw+'='*((-len(raw))%4),altchars=b'-_',validate=True)
        if len(decoded)>64000:raise ValueError('Message exceeds its MIME byte budget.')
        message=BytesParser(policy=policy.default).parsebytes(decoded)
        parts=list(message.walk())
        if len(parts)>32:raise ValueError('Message exceeds its MIME part budget.')
        texts=[];omitted=[]
        for part in parts:
            if part.is_multipart():continue
            if part.get_filename() or part.get_content_disposition()=='attachment':omitted.append('attachment');continue
            if part.get_content_type()!='text/plain':omitted.append(part.get_content_type());continue
            content=part.get_content()
            if not isinstance(content,str):raise ValueError('Message text could not be decoded.')
            texts.append(content)
        text='\n'.join(texts)
        return [dict(id=resource,**{k:str(message.get(k,''))[:1000] for k in ['subject','from','to','date']},text=text[:6000],coverage='plain_text_parts_only',omitted_parts=sorted(set(omitted)),possibly_truncated=len(text)>6000,html_only=not texts and 'text/html' in omitted)]
    if service=='docs_text':
        if data.get('documentId')!=resource:raise ValueError('Returned document identity differs.')
        content=data.get('body',{}).get('content',[])
        if not isinstance(content,list) or len(content)>2000:raise ValueError('Document exceeds its paragraph budget.')
        text=''.join(str(e.get('textRun',{}).get('content','')) for p in content if isinstance(p,dict) for e in p.get('paragraph',{}).get('elements',[]) if isinstance(e,dict))
        return [dict(id=resource,title=str(data.get('title',''))[:500],text=text[:12000],coverage='first_tab_paragraph_text_only',possibly_truncated=len(text)>12000,excluded=['other_tabs','tables','images','suggested_changes'])]
    if service=='sheets_values':
        requested=cell_range(selected_range);returned=cell_range(data.get('range'))
        if requested['normalized']!=returned['normalized']:raise ValueError('Returned sheet range differs.')
        values=data.get('values',[])
        if not isinstance(values,list) or len(values)>requested['height'] or any(not isinstance(row,list) or len(row)>requested['width'] for row in values):raise ValueError('Sheet values exceed the selected rectangle.')
        if any(type(v) not in (str,int,float,bool) or isinstance(v,str) and len(v)>2000 for row in values for v in row):raise ValueError('Unsupported or oversized sheet value.')
        return [dict(id=resource,range=returned['normalized'],values=values,coverage='selected_formatted_values_only',possibly_truncated=False)]
    raise ValueError('Unsupported Google content projection.')
