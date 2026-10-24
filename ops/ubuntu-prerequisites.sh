#!/usr/bin/env bash
set -euo pipefail
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || { echo 'Expected the project Ubuntu 24.04 environment.' >&2; exit 1; }
[[ "$EUID" == 0 ]] || { echo 'Run this prerequisite step as root in the project distribution.' >&2; exit 1; }
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl git binutils zstd xz-utils python3 python3-venv python3-pip openssh-client unzip
if ! id assistant >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash assistant
fi
# The account remains password-locked and is not added to sudo.
id assistant
echo 'Prerequisites installed. Run the agent stack as the unprivileged assistant account.'
