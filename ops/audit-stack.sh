#!/usr/bin/env bash
set -euo pipefail
. "$HOME/.nvm/nvm.sh"
case "${1:-host}" in
  host) cd "$HOME/.nemoclaw/source"; report_name=runtime-audit.json ;;
  plugin) cd "$HOME/.nemoclaw/source/nemoclaw"; report_name=plugin-runtime-audit.json ;;
  *) exit 2 ;;
esac
status=0
npm audit --omit=dev --json > "$HOME/ai-assistant-install/$report_name" || status=$?
[[ "$status" -le 1 ]] || { echo 'npm audit could not complete.' >&2; exit "$status"; }
node - "$HOME/ai-assistant-install/$report_name" <<'NODE'
const fs = require('node:fs');
const report = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
console.log(JSON.stringify({metadata: report.metadata, error: report.error,
  packages: Object.entries(report.vulnerabilities || {}).map(([name,v]) => ({name,
    severity:v.severity, direct:v.isDirect, range:v.range, fixAvailable:v.fixAvailable,
    advisories:v.via.filter(a => typeof a === 'object').map(a=>({title:a.title,url:a.url,range:a.range}))}))}, null, 2));
NODE
