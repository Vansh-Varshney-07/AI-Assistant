import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {expect,it} from 'vitest';
const root=path.resolve(import.meta.dirname,'..');
const sha=(value:Buffer|string)=>createHash('sha256').update(value).digest('hex');

it('binds the original SVG manifest to the vetted source without external content',()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'resources/visual-assets.json'),'utf8'));
  const source=fs.readFileSync(path.join(root,'src/renderer/Onboarding.tsx'),'utf8');
  const svg=source.match(/<svg viewBox="0 0 360 190".*?<\/svg>/s)![0];
  expect(sha(svg)).toBe(manifest.assets[0].content_sha256);
  expect(svg).not.toMatch(/<script|foreignObject|<image|\son[a-z]+=|(?:href|url)\s*[=(]/i);
  expect(manifest.runtime_remote_requests).toBe(false);
});

it('retains the actual notices and integrity hashes for every packaged dependency',()=>{
  const folder=path.join(root,'resources/licenses/javascript');
  const index=JSON.parse(fs.readFileSync(path.join(folder,'index.json'),'utf8'));
  expect(index.packages.some((item:any)=>item.name==='react-markdown'&&item.version==='10.1.0')).toBe(true);
  expect(index.packages.some((item:any)=>item.name==='remark-gfm'&&item.version==='4.0.1')).toBe(true);
  for(const item of index.packages)for(const notice of item.notices){
    const file=path.resolve(folder,notice.file);expect(path.dirname(file)).toBe(folder);
    expect(sha(fs.readFileSync(file))).toBe(notice.sha256);
  }
});
