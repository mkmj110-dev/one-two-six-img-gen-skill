#!/usr/bin/env bash
set -euo pipefail

TARGET="${TARGET:-all}"
REPO="${REPO:-mkmj110-dev/one-two-six-img-gen-skill}"
REF="${REF:-main}"
SKILL_NAME="126-img-gen"

case "$TARGET" in
  all|codex|claude) ;;
  *)
    echo "TARGET must be one of: all, codex, claude" >&2
    exit 2
    ;;
esac

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 2
  fi
}

install_skill() {
  local destination_root="$1"
  local destination="$destination_root/$SKILL_NAME"
  mkdir -p "$destination_root"

  if [ -e "$destination" ]; then
    local backup="$destination.bak-$(date +%Y%m%d%H%M%S)"
    mv "$destination" "$backup"
    echo "Backed up existing skill: $backup"
  fi

  cp -R "$SKILL_SOURCE" "$destination"
  echo "Installed $SKILL_NAME -> $destination"
}

require_cmd curl
require_cmd python3

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

ZIP_PATH="$TMP_DIR/skill.zip"
EXTRACT_PATH="$TMP_DIR/extract"
mkdir -p "$EXTRACT_PATH"

URL="https://codeload.github.com/$REPO/zip/refs/heads/$REF"
echo "Downloading $URL"
curl -fsSL "$URL" -o "$ZIP_PATH"

python3 - "$ZIP_PATH" "$EXTRACT_PATH" <<'PY'
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1])
extract_path = Path(sys.argv[2])
with zipfile.ZipFile(zip_path) as archive:
    archive.extractall(extract_path)
PY

SKILL_SOURCE="$(find "$EXTRACT_PATH" -type f -name SKILL.md -path "*/126-img-gen/SKILL.md" -print -quit | xargs dirname)"
if [ -z "$SKILL_SOURCE" ] || [ ! -f "$SKILL_SOURCE/SKILL.md" ]; then
  echo "Could not find 126-img-gen/SKILL.md in downloaded archive." >&2
  exit 1
fi

if [ "$TARGET" = "all" ] || [ "$TARGET" = "codex" ]; then
  install_skill "$HOME/.codex/skills"
fi

if [ "$TARGET" = "all" ] || [ "$TARGET" = "claude" ]; then
  install_skill "$HOME/.claude/skills"
fi

echo
echo "Done. Restart Codex if it was already open. Claude Code usually detects skill changes automatically."
echo "Set ONE_TWO_SIX_API_KEY before using the skill."
