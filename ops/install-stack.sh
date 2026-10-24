#!/usr/bin/env bash
set -euo pipefail
[[ "$EUID" != 0 ]] || { echo 'Run this as the project assistant account, not root.' >&2; exit 1; }
command -v docker >/dev/null || { echo 'Enable Docker Desktop integration for the project distro first.' >&2; exit 1; }
docker info >/dev/null || { echo 'Docker is not reachable. No installer was run.' >&2; exit 1; }
export NEMOCLAW_AGENT=hermes
export NEMOCLAW_SANDBOX_NAME=ai-assistant
export NEMOCLAW_DISABLE_TELEMETRY=1
export NEMOCLAW_NO_EXPRESS=1
export NEMOCLAW_SINGLE_SESSION=1
export NEMOCLAW_INSTALL_REF=f00fb1dafe2113940b89bcd82f0561adf2696a7b
setup_dir="$HOME/ai-assistant-install"
mkdir -p "$setup_dir"
curl -fsSL --proto '=https' --proto-redir '=https' \
  "https://raw.githubusercontent.com/NVIDIA/NemoClaw/${NEMOCLAW_INSTALL_REF}/install.sh" \
  -o "$setup_dir/install.sh"
bash -n "$setup_dir/install.sh"
# This installs the managed host CLI and its compatible OpenShell dependency.
# Hermes is supplied inside the sandbox during later authenticated onboarding.
# Defer mode creates no provider or sandbox and performs no model call.
bash "$setup_dir/install.sh" --defer-onboarding
# The installer runs in a child shell; load its user-local executables here.
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
  . "$HOME/.nvm/nvm.sh"
fi
hash -r
command -v nemohermes
nemohermes --version
openshell --version
