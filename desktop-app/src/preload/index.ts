import { contextBridge, ipcRenderer } from 'electron';
import type { DesktopAPI } from '../shared/types';
import release from '../../FEATURES.json';

// No generic invoke, HTTP, filesystem, shell, approval token or event object.
const methods = release.preload_methods as (keyof DesktopAPI)[];
const api = Object.fromEntries(methods.map(name => [name, async (...args: unknown[]) => { const response = await ipcRenderer.invoke(`wayfinder:${name}`, ...args); if (!response?.ok) throw new Error(response?.error || 'Request failed.'); return response.data; }])) as unknown as DesktopAPI;
contextBridge.exposeInMainWorld('wayfinder', Object.freeze(api));
