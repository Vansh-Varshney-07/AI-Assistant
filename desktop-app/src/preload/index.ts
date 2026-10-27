import { contextBridge, ipcRenderer } from 'electron';
import type { DesktopAPI } from '../shared/types';

// No generic invoke, HTTP, filesystem, shell, approval token or event object.
const methods = [
  'status', 'connect', 'listSpaces', 'createSpace', 'inventory', 'source', 'recall', 'context',
  'proposeMemory', 'reviewMemory', 'rejectMemory', 'reconcileMemory', 'revokeMemory',
  'inspectRuntime', 'capabilities', 'selectFiles', 'fileSelection', 'searchFiles', 'revokeFiles', 'analyze', 'compare',
  'snapshot', 'run', 'cancel', 'clearRun', 'audit', 'evaluate', 'retryRead', 'readActivity',
  'selectRepository', 'repositorySelection', 'observeRepository', 'proposeBranch', 'reviewBranch', 'rejectBranch',
  'reconcileBranch', 'revokeRepository', 'revokeBranch', 'googleStatus', 'getSettings', 'setFontSize',
] as const;
const api = Object.fromEntries(methods.map(name => [name, async (...args: unknown[]) => { const response = await ipcRenderer.invoke(`wayfinder:${name}`, ...args); if (!response?.ok) throw new Error(response?.error || 'Request failed.'); return response.data; }])) as unknown as DesktopAPI;
contextBridge.exposeInMainWorld('wayfinder', Object.freeze(api));
