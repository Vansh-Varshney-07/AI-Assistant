#!/usr/bin/env bash
set -euo pipefail
[[ "$(id -un)" == assistant ]] || { echo 'Run as the project assistant account.' >&2; exit 1; }
# Use Linux tools, avoiding Windows npm inherited through WSL interoperability.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export NVM_DIR="$HOME/.nvm"
if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  installer="$(mktemp)"
  trap 'rm -f "$installer"' EXIT
  curl -fsSL --proto '=https' --proto-redir '=https' \
    https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh -o "$installer"
  printf '%s  %s\n' 4b7412c49960c7d31e8df72da90c1fb5b8cccb419ac99537b737028d497aba4f "$installer" | sha256sum --check --status
  bash "$installer"
fi
. "$NVM_DIR/nvm.sh"
nvm install 22 --no-progress
nvm alias default 22
if [[ ! -e "$HOME/ai-assistant" && ! -L "$HOME/ai-assistant" ]]; then
  ln -s '/mnt/d/Opencode_/AI assistant' "$HOME/ai-assistant"
fi
node --version
npm --version
python3 --version
git --version
