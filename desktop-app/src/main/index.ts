import { app, BrowserWindow, dialog, ipcMain, Menu, session } from 'electron';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { BackendBridge } from './bridge';
import { createHandlers } from './broker';
import { requireMainSender } from './sender';
import { existsSync } from 'node:fs';
import { runtimeChoice } from './runtime-path';
import release from '../../FEATURES.json';

declare const WAYFINDER_SOURCE_ROOT: string;
const appDirectory = path.dirname(fileURLToPath(import.meta.url));
const project = process.env.WAYFINDER_PROJECT_ROOT || WAYFINDER_SOURCE_ROOT;
// Hidden verification is a presentation-only test mode, with an isolated profile.
const hiddenVerification = process.env.WAYFINDER_VERIFY_HIDDEN === '1';
if (process.env.WAYFINDER_VERIFY_PROFILE && path.isAbsolute(process.env.WAYFINDER_VERIFY_PROFILE)) app.setPath('userData', process.env.WAYFINDER_VERIFY_PROFILE);
const selected = runtimeChoice({ packaged: app.isPackaged, project, userData: app.getPath('userData'), explicit: process.env.WAYFINDER_DESKTOP_RUNTIME, exists: existsSync });
const runtime = selected.root;
const host = app.isPackaged ? path.join(process.resourcesPath, 'backend', 'host.py') : path.join(project, 'desktop-app', 'backend', 'host.py');
const bridge = new BackendBridge(project, host, runtime, selected.error);
let main: BrowserWindow | undefined, quitting = false;
if (!app.requestSingleInstanceLock({ runtime })) app.quit();
else {
  app.on('second-instance', (_event, _argv, _cwd, data) => {
    if (!main) return;
    if (main.isMinimized()) main.restore();
    main.show(); main.focus();
    const requested = data && typeof data === 'object' && 'runtime' in data ? data.runtime : undefined;
    if (typeof requested === 'string' && requested !== runtime) void dialog.showMessageBox(main, { message: 'Another runtime was not opened', detail: 'This app already owns a selected runtime. Quit Wayfinder before opening a different data directory. No data was switched or copied.' });
  });
  app.whenReady().then(() => {
    app.setAppUserModelId('local.wayfinder.desktop');
    const rendererFile = path.resolve(appDirectory, '../renderer/index.html');
    const rendererURL = pathToFileURL(rendererFile).href;
    main = new BrowserWindow({
      width: 1440, height: 940, minWidth: 600, minHeight: 600, show: !hiddenVerification, title: 'Wayfinder', backgroundColor: '#11171c', icon: app.isPackaged ? path.join(process.resourcesPath, 'wayfinder.png') : path.join(project, 'desktop-app/resources/wayfinder.png'),
      webPreferences: { preload: path.join(appDirectory, '../preload/index.cjs'), contextIsolation: true, nodeIntegration: false, sandbox: true, webSecurity: true, allowRunningInsecureContent: false, spellcheck: false },
    });
    main.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
    main.webContents.on('will-navigate', event => event.preventDefault());
    main.webContents.on('will-attach-webview', event => event.preventDefault());
    session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
    session.defaultSession.setPermissionCheckHandler(() => false);
    const handlers = createHandlers(bridge, {
      pick: async kind => {
        const result = await dialog.showOpenDialog(main!, {
          title: kind === 'repository' ? 'Select a repository for the bounded local branch operation' : kind === 'folder' ? 'Select a read-only folder' : kind === 'activity' ? 'Select a canonical activity CSV' : 'Select one document',
          properties: kind === 'folder' || kind === 'repository' ? ['openDirectory'] : ['openFile'],
          filters: kind === 'document' ? [{ name: 'Text documents', extensions: ['txt', 'md', 'csv', 'json', 'log'] }] : kind === 'activity' ? [{ name: 'Canonical CSV', extensions: ['csv'] }] : [],
        });
        return result.canceled ? null : result.filePaths[0] || null;
      },
      confirm: async (title, detail) => (await dialog.showMessageBox(main!, { type: 'question', title, message: title, detail, buttons: ['Cancel', 'Approve exact change once'], defaultId: 0, cancelId: 0, noLink: true, normalizeAccessKeys: true })).response === 1,
    }, { status: () => bridge.describe(), connect: () => bridge.connect() });
    for (const [method, handler] of Object.entries(handlers)) ipcMain.handle(`wayfinder:${method}`, async (event, ...args) => {
      if (!release.preload_methods.includes(method)) throw new Error('Intent is not included in this build.');
      if (!main) throw new Error('Window unavailable.');
      requireMainSender(event, main.webContents, rendererURL);
      if (Buffer.byteLength(JSON.stringify(args)) > 65536) throw new Error('Desktop request too large.');
      try { return { ok: true, data: await handler(...args) }; }
      catch (error) { return { ok: false, error: error instanceof Error ? error.message : 'Request failed. No completion is asserted.' }; }
    });
    Menu.setApplicationMenu(Menu.buildFromTemplate([
      { label: 'Wayfinder', submenu: [{ label: 'About Wayfinder', click: () => dialog.showMessageBox(main!, { message: 'Wayfinder · Memory and evidence', detail: 'A desktop client for completed local backend capabilities. General chat, scheduling, Google live access and native desktop actions are not included in this build.' }) }, { type: 'separator' }, { role: 'quit' }] },
      { role: 'editMenu' }, { role: 'viewMenu' },
    ]));
    main.loadFile(rendererFile);
    void bridge.connect();
  });
  app.on('window-all-closed', () => app.quit());
  app.on('before-quit', event => {
    if (quitting) return;
    event.preventDefault(); quitting = true;
    void bridge.close().finally(() => app.quit());
  });
}
