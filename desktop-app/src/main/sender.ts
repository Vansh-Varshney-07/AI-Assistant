/** Used by the actual IPC handler and directly exercised by boundary tests. */
export function requireMainSender(event: { sender: unknown; senderFrame: { url: string } | null }, contents: { mainFrame: unknown }, expectedURL: string) {
  if (event.sender !== contents || event.senderFrame !== contents.mainFrame || event.senderFrame?.url !== expectedURL) throw new Error('Untrusted desktop sender.');
}
