import { execFileSync } from 'node:child_process';
import { homedir } from 'node:os';
import { writeFileSync } from 'node:fs';

const env = {...process.env, NEMOCLAW_DISABLE_TELEMETRY: '1'};
const result = {timestamp: new Date().toISOString(), sandbox: 'ai-assistant'};
const output = '/mnt/d/Opencode_/AI assistant/.local/hermes-smoke-results.json';
try {
  // Capture the local bearer token without printing or persisting it.
  const token = execFileSync(`${homedir()}/.local/bin/nemohermes`,
    ['ai-assistant', 'gateway-token', '--quiet'],
    {env, encoding: 'utf8', timeout: 30000, stdio: ['ignore', 'pipe', 'ignore']}).trim();
  if (!token || /\s/.test(token)) throw new Error('Local API token could not be obtained.');
  const dashboard = await fetch('http://127.0.0.1:18789/', {signal: AbortSignal.timeout(15000)});
  result.dashboardHttp = dashboard.status;
  result.dashboardHtml = /<html/i.test(await dashboard.text());
  const auth = {Authorization: `Bearer ${token}`, 'Content-Type': 'application/json'};
  const modelsResponse = await fetch('http://127.0.0.1:8642/v1/models',
    {headers: auth, signal: AbortSignal.timeout(15000)});
  result.modelsHttp = modelsResponse.status;
  if (!modelsResponse.ok) throw new Error('Authenticated model listing failed.');
  const models = await modelsResponse.json();
  const model = models.data?.[0]?.id;
  if (!model) throw new Error('The local API did not advertise a model.');
  result.apiModel = model;
  const base = {model, max_tokens: 512, stream: false};
  const endpoint = 'http://127.0.0.1:8642/v1/chat/completions';
  const unauth = await fetch(endpoint, {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({...base, messages: [{role: 'user', content: 'Reply with AUTH_CHECK.'}]}),
    signal: AbortSignal.timeout(20000)});
  result.unauthenticatedHttp = unauth.status;
  await unauth.arrayBuffer();
  if (![401,403].includes(unauth.status)) throw new Error('The local chat API did not reject an unauthenticated request.');
  const chat = await fetch(endpoint, {method: 'POST', headers: auth,
    body: JSON.stringify({...base, messages: [{role: 'user', content: 'Reply exactly SETUP_SMOKE_OK. Do not use tools.'}]}),
    signal: AbortSignal.timeout(180000)});
  result.chatHttp = chat.status;
  if (!chat.ok) throw new Error('Authenticated chat request failed.');
  const reply = await chat.json();
  result.chatMarker = reply.choices?.[0]?.message?.content?.includes('SETUP_SMOKE_OK') === true;
  if (!result.chatMarker) throw new Error('The chat reply did not contain the expected marker.');
  const toolChat = await fetch(endpoint, {method: 'POST', headers: auth,
    body: JSON.stringify({...base, messages: [{role: 'user', content:
      'Use the terminal tool to write the exact text SETUP_TOOL_OK into /sandbox/setup-smoke-tool.txt, then reply SETUP_TOOL_DONE. Do not delegate or access the network except for your model connection.'}]}),
    signal: AbortSignal.timeout(180000)});
  result.toolChatHttp = toolChat.status;
  if (!toolChat.ok) throw new Error('Tool execution request failed.');
  const toolReply = await toolChat.json();
  result.toolReplyMarker = toolReply.choices?.[0]?.message?.content?.includes('SETUP_TOOL_DONE') === true;
  result.apiChecksPassed = result.dashboardHttp === 200 && result.dashboardHtml && result.chatMarker && result.toolReplyMarker;
  result.toolArtifactNeedsIndependentCheck = true;
} catch (error) {
  result.apiChecksPassed = false;
  result.error = error.message?.replace(/Bearer\s+\S+/g, 'Bearer [redacted]');
  process.exitCode = 1;
}
writeFileSync(output, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
