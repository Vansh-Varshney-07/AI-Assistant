import { app, BrowserWindow, dialog, ipcMain, Menu, session } from 'electron';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { BackendBridge } from './bridge';
import { createHandlers } from './broker';
import { requireMainSender } from './sender';

declare const WAYFINDER_SOURCE_ROOT: string;
const appDirectory = path.dirname(fileURLToPath(import.meta.url));
const project = process.env.WAYFINDER_PROJECT_ROOT || WAYFINDER_SOURCE_ROOT;
const runtime = process.env.WAYFINDER_DESKTOP_RUNTIME || path.join(project, '.local', 'wayfinder-electron');
const host = app.isPackaged ? path.join(process.resourcesPath, 'backend', 'host.py') : path.join(project, 'desktop-app', 'backend', 'host.py');
const bridge = new BackendBridge(project, host, runtime);
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
      width: 1440, height: 940, minWidth: 720, minHeight: 600, title: 'Wayfinder', backgroundColor: '#17181b', icon: app.isPackaged ? path.join(process.resourcesPath, 'wayfinder.png') : path.join(project, 'desktop-app/resources/wayfinder.png'),
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
