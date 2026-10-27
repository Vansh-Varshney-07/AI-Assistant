"""Document-only checks and final packaging; does not run the memory application."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import shutil
import unicodedata
from docx import Document
from pypdf import PdfReader

base = Path(__file__).resolve().parent
out = base / 'manuscript/reconstructed'
target = out/'Iron_Web_Complete_Research_Paper.docx'
pdf = out/'Iron_Web_Complete_Research_Paper.pdf'
shutil.copyfile(out/'qa/manuscript.pdf',pdf)
doc = Document(target)
reader = PdfReader(pdf)
assert len(reader.pages)==9
assert len(doc.tables)==2 and len(doc.inline_shapes)==1
headings = [p.text for p in doc.paragraphs if p.style.name=='Heading 1']
assert len(headings)==len(set(headings))==13
assert len([h for h in headings if re.match(r'^\d+\.',h)])==10
assert doc.styles['Normal'].font.size.pt == 15
assert doc.styles['Normal'].font.name == 'Times New Roman'
full = '\n'.join(p.extract_text() for p in reader.pages)
full = re.sub(r'Iron Web \| Architecture and implementation study \|\s*\d+','',full)
def norm(s):
    s = unicodedata.normalize('NFKD',s)
    return re.sub(r'[^a-z0-9]','',s.lower())
pdfnorm = norm(full)
claimmap = json.loads((out/'paper_claim_map.json').read_text(encoding='utf-8'))
missing = [p['id'] for p in claimmap['paragraphs'] if norm(p['text']) not in pdfnorm]
assert not missing, missing
for table,expected in zip(doc.tables,claimmap['tables']):
    actual = [[c.text for c in row.cells] for row in table.rows]
    assert actual == [expected['headers']]+[[str(v) for v in r] for r in expected['rows']]
refs = json.loads((out/'reference_verification.json').read_text(encoding='utf-8'))
assert [r['number'] for r in refs] == list(range(1,13))
text = '\n'.join(p.text for p in doc.paragraphs)
body = text.split('References')[0]
assert '[cite:' not in text
observed = list(dict.fromkeys(map(int,re.findall(r'\[(\d+)\]',body))))
assert observed == list(range(1,13)), observed
original = base/'manuscript/Iron_Web_Research_Paper_9_Page_Editing_Draft.docx'
manifest = json.loads((out/'generation_manifest.json').read_text())
assert hashlib.sha256(original.read_bytes()).hexdigest() == manifest['original_sha256']
manifest.update({
    'pdf_render':'Microsoft Word native ExportAsFixedFormat; standard renderer unavailable because LibreOffice is absent',
    'pdf_pages':len(reader.pages),
    'visual_inspection':{'pages':[1,2,3,4,5,6,7,8,9],'status':'passed','details':'All final page PNGs inspected. Diagram readable, tables aligned and complete, references left aligned, no blank pages, clipped text, repeated headings or unfinished result placeholders.'},
    'document_checks':{'all_mapped_paragraphs_present_in_pdf':True,'table_cells_match_audited_data':True,'references_numbered_in_first_citation_order':True,'original_backup_unchanged':True,'main_headings_unique':True,'body_font_points':15},
})
paths = [target,pdf,out/'paper_claim_evidence_audit.md',out/'paper_generation_notes.md',out/'paper_claim_map.json',out/'reference_verification.json']
notes = out/'paper_generation_notes.md'
notes.write_text(notes.read_text(encoding='utf-8')+'\n## Final document verification\n\nThe final Word export has **nine pages**. All nine rendered pages were visually inspected. Every mapped body paragraph survives PDF extraction; both tables match the audited source values, all twelve references follow first-citation order, and the original draft hash remains unchanged.\n',encoding='utf-8')
manifest['outputs'] = [{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
(out/'generation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
# Remove only the obsolete tenth-page preview from the earlier, superseded render.
stale = out/'qa/page-10.png'
if stale.is_file():
    stale.unlink()
print(json.dumps({'pages':len(reader.pages),'paragraphs_verified':len(claimmap['paragraphs']),'references':len(refs),'tables':len(doc.tables),'original_unchanged':True,'output':str(out)},indent=2))
