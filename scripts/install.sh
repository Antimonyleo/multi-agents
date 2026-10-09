#!/usr/bin/env bash
# Link this repo's skill and agents into ~/.claude so Claude Code loads them from here.
# Usage: scripts/install.sh [--check | --uninstall]     (default: install)
# CLAUDE_HOME overrides the target (default ~/.claude), for testing.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="${CLAUDE_HOME:-$HOME/.claude}"
mode="${1:-install}"
pairs=("$REPO/skill/scientific-workflow|$CLAUDE/skills/scientific-workflow")
for f in "$REPO"/agents/scientific_*.md; do pairs+=("$f|$CLAUDE/agents/$(basename "$f")"); done
status=0
for pair in "${pairs[@]}"; do
  src="${pair%%|*}"; dst="${pair##*|}"
  mine=false; { [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; } && mine=true
  case "$mode" in
    install)
      mkdir -p "$(dirname "$dst")"
      if $mine; then echo "ok       $dst"
      elif [ -e "$dst" ] || [ -L "$dst" ]; then echo "SKIPPED  $dst exists and is not a link to this repo; move it away first"; status=1
      else ln -s "$src" "$dst"; echo "linked   $dst -> $src"; fi ;;
    --check)
      if $mine && [ -e "$dst" ]; then echo "ok       $dst"; else echo "MISSING  $dst"; status=1; fi ;;
    --uninstall)
      if $mine; then rm "$dst"; echo "removed  $dst"; else echo "skipped  $dst (not a link to this repo)"; fi ;;
    *) echo "usage: $0 [--check|--uninstall]"; exit 2 ;;
  esac
done
[ "$mode" = install ] && echo "Settings are not touched: merge settings/settings.snippet.json into $CLAUDE/settings.json by hand."
exit $status
