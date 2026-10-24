#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Building and installing KeepMeUp..."
"$SCRIPT_DIR/scripts/build_release.sh" --install
