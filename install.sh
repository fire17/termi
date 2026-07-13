#!/bin/sh
# termi installer — POSIX sh, cross-platform (macOS · Linux · WSL).
# Idempotent (ORACLE I6). Detects the environment and shows verified coverage.
set -eu

here=$(cd "$(dirname "$0")" && pwd)

case "$(uname -s)" in
  Darwin) os=macos ;;
  Linux)  if grep -qi microsoft /proc/version 2>/dev/null; then os=wsl; else os=linux; fi ;;
  *)      os="$(uname -s)" ;;
esac

# ORACLE P1 — python3 >= 3.11 with tomllib, before anything else
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import tomllib' 2>/dev/null; then
  echo "termi needs Python >= 3.11."
  if [ "$os" = macos ]; then
    echo "  fix: xcode-select --install   (or: brew install python3)"
  else
    echo "  fix: sudo apt-get update && sudo apt-get install -y python3"
  fi
  exit 2
fi

mkdir -p "$HOME/.local/bin"
ln -sf "$here/bin/termi" "$HOME/.local/bin/termi"
chmod +x "$here/bin/termi"
echo "✓ termi installed → ~/.local/bin/termi   ($os)"

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "add to PATH first:  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

echo ""
# the post-install message IS the live environment report + agent one-liner
exec "$here/bin/termi" env
