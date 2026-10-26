import {it,expect} from 'vitest';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {ConnectionVault,validateConnections} from '../src/main/connection-vault';
const crypto={available:async()=>true,encrypt:async(s:string)=>Buffer.from('FIXTURE:'+Buffer.from(s).toString('base64')),decrypt:async(b:Buffer)=>Buffer.from(b.toString().slice(8),'base64').toString()};
it('imports only supported values and never returns credentials',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'wayfinder-vault-fixture-')),profile=path.join(root,'profile'),source=path.join(root,'.env');
  await fs.writeFile(source,'TAVILY_API_KEY=PRIVATE_TAVILY_FIXTURE\nNOTION_API_KEY=PRIVATE_NOTION_FIXTURE\nGEMINI_API_KEY=NEVER_IMPORT_THIS\n');
  const vault=new ConnectionVault(profile,crypto),status=await vault.importFile(source);
  expect(status.configured).toEqual({google:false,tavily:true,notion:true});expect(JSON.stringify(status)).not.toContain('PRIVATE');
  const raw=await fs.readFile(vault.file,'utf8');expect(raw).not.toContain('PRIVATE_TAVILY');expect(raw).not.toContain('NEVER_IMPORT');
  const restarted=new ConnectionVault(profile,crypto);await restarted.load();expect(restarted.status().configured.notion).toBe(true);
  await restarted.disconnect('tavily');expect(restarted.status().configured.tavily).toBe(false);
});
it('does not fall back to plaintext when encryption is unavailable',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'wayfinder-vault-unavailable-'));await fs.writeFile(path.join(root,'.env'),'TAVILY_API_KEY=fixture');
  const vault=new ConnectionVault(path.join(root,'profile'),{...crypto,available:async()=>false});await expect(vault.importFile(path.join(root,'.env'))).rejects.toThrow(/encryption is unavailable/);await expect(fs.stat(vault.file)).rejects.toThrow();
});
it('rejects Google refresh endpoints and referenced credential scope escapes',async()=>{
  expect(()=>validateConnections({schema:1,google:JSON.stringify({token_uri:'https://attacker.invalid/token',scopes:[]}),tavily:null,notion:null})).toThrow(/Google needs/);
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'wayfinder-vault-scope-'));await fs.writeFile(path.join(root,'.env'),'GOOGLE_WORKSPACE_TOKEN_PATH=../outside-token.json');
  await expect(new ConnectionVault(path.join(root,'profile'),crypto).importFile(path.join(root,'.env'))).rejects.toThrow(/within the selected project/);
});
