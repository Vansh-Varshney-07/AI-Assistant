import path from 'node:path';

/** A packaged executable's location must never select a new unexplained store. */
export function runtimeChoice(options: { packaged: boolean; project: string; userData: string; explicit?: string; exists: (path: string) => boolean }): { root: string; error?: string } {
  const development = path.join(options.project, '.local', 'wayfinder-electron');
  const stable = path.join(options.userData, 'runtime');
  if (options.explicit) {
    if (!path.isAbsolute(options.explicit)) return { root: stable, error: 'Runtime selection must be an absolute path. No fallback store was opened.' };
    return { root: path.resolve(options.explicit) };
  }
  if (!options.packaged) return { root: development };
  if (!options.exists(stable) && options.exists(development)) return { root: stable, error: 'An existing development data directory was found. Quit and explicitly select it with Start.ps1 -Runtime, or arrange a reviewed migration. No new store was opened and no existing data was copied.' };
  return { root: stable };
}
