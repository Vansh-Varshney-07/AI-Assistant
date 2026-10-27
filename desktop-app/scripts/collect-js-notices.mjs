// Bundle the actual notices shipped with production dependencies. No downloads.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const lock=JSON.parse(await fs.readFile(path.join(root,'package-lock.json'),'utf8'));
const output=path.join(root,'resources/licenses/javascript');await fs.mkdir(output,{recursive:true});
const packages=[];
for(const [relative,entry] of Object.entries(lock.packages)){
  if(!relative||entry.dev||entry.devOptional)continue;
  const folder=path.join(root,relative),metadata=JSON.parse(await fs.readFile(path.join(folder,'package.json'),'utf8'));
  const names=(await fs.readdir(folder,{withFileTypes:true})).filter(file=>file.isFile()&&/^(licen[cs]e(?:\..*)?|notice(?:\..*)?|copying(?:\..*)?)$/i.test(file.name));
  if(!names.length)throw new Error(`Missing packaged notice: ${metadata.name}`);
  const notices=[];
  for(const file of names){const raw=await fs.readFile(path.join(folder,file.name));const name=metadata.name.replaceAll('/','__')+'-'+file.name+'.txt';await fs.writeFile(path.join(output,name),raw);notices.push({file:name,sha256:createHash('sha256').update(raw).digest('hex')});}
  packages.push({name:metadata.name,version:metadata.version,license:metadata.license,registry_integrity:entry.integrity,notices});
}
await fs.writeFile(path.join(output,'index.json'),JSON.stringify({schema:'wayfinder.javascript-notices/1',packages},null,2)+'\n');
console.log(`Collected notices for ${packages.length} installed production packages`);
