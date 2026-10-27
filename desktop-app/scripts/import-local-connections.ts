/** Developer-owned, headless import using the exact production vault implementation. */
import {app,safeStorage} from 'electron';
import path from 'node:path';
import {ConnectionVault} from '../src/main/connection-vault';
const [source,profile]=process.argv.slice(2);
app.setName('wayfinder-desktop');
if(profile){if(!path.isAbsolute(profile))throw new Error('Absolute profile required.');app.setPath('userData',profile);}
app.whenReady().then(async()=>{
  if(process.platform!=='win32'||!source||!path.isAbsolute(source))throw new Error('Windows and an explicit local credential file are required.');
  const vault=new ConnectionVault(app.getPath('userData'),{available:()=>safeStorage.isAsyncEncryptionAvailable(),encrypt:value=>safeStorage.encryptStringAsync(value),decrypt:async value=>(await safeStorage.decryptStringAsync(value)).result});
  await vault.load();await vault.importFile(source);console.log('WAYFINDER_IMPORT='+JSON.stringify({...vault.status(),profile:app.getPath('userData')}));app.quit();
}).catch(()=>{console.error('Credential import was not completed. Existing source files were preserved; no secret values were printed.');app.exit(1);});
