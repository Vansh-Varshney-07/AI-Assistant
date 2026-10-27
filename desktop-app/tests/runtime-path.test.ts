import { expect, it } from 'vitest';
import path from 'node:path';
import { runtimeChoice } from '../src/main/runtime-path';
const base = { packaged: true, project: path.resolve('project'), userData: path.resolve('profile') };
it('packaged data identity is stable when the executable/project moves', () => {
  const a = runtimeChoice({ ...base, exists: () => false });
  const b = runtimeChoice({ ...base, project: path.resolve('moved-project'), exists: () => false });
  expect(a.root).toBe(b.root); expect(a.error).toBeUndefined();
});
it('does not create an empty replacement when a development root already exists', () => {
  const result = runtimeChoice({ ...base, exists: p => p.endsWith('wayfinder-electron') });
  expect(result.error).toMatch(/No new store/);
});
it('explicit absolute root selection wins without fallback', () => {
  const explicit = path.resolve('selected-runtime');
  expect(runtimeChoice({ ...base, explicit, exists: () => false })).toEqual({ root: explicit });
  expect(runtimeChoice({ ...base, explicit: 'relative-runtime', exists: () => false }).error).toMatch(/absolute/);
});
