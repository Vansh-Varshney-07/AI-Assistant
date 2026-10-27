import { expect, it } from 'vitest';
import { requireMainSender } from '../src/main/sender';
it('only the owned app main frame may invoke a privileged method', () => {
  const frame = { url: 'file:///app/index.html' }, contents = { mainFrame: frame };
  expect(() => requireMainSender({ sender: contents, senderFrame: frame }, contents, frame.url)).not.toThrow();
  expect(() => requireMainSender({ sender: {}, senderFrame: frame }, contents, frame.url)).toThrow('Untrusted');
  expect(() => requireMainSender({ sender: contents, senderFrame: { url: frame.url } }, contents, frame.url)).toThrow('Untrusted');
  expect(() => requireMainSender({ sender: contents, senderFrame: null }, contents, frame.url)).toThrow('Untrusted');
  expect(() => requireMainSender({ sender: contents, senderFrame: frame }, contents, 'https://forged.example')).toThrow('Untrusted');
});
