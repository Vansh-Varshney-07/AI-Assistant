import { expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { createHandlers } from '../src/main/broker';
it('every exposed preload intent has one actual privileged handler, with no generic escape hatch', () => {
  const source = readFileSync(path.resolve(process.cwd(), 'src/preload/index.ts'), 'utf8');
  const definition = source.match(/const methods = \[([\s\S]*?)\] as const/)![1];
  const names = [...definition.matchAll(/'([A-Za-z]+)'/g)].map(match => match[1]);
  const handlers = createHandlers({ call: vi.fn() }, { pick: vi.fn(), confirm: vi.fn() }, { status: vi.fn(), connect: vi.fn() });
  expect(new Set(names)).toEqual(new Set(Object.keys(handlers)));
  expect(names).not.toContain('invoke'); expect(names).not.toContain('exec'); expect(names).not.toContain('call');
});
