#!/bin/bash
# Drain the email-clipper inbox: convert every .eml in INBOX to a vault note,
# then move it to processed/ (or failed/ on error).
#
# Triggered by the launchd WatchPaths agent at:
#   ~/Library/LaunchAgents/com.bryan.email-clipper.plist
#
# Configurable via env (overrideable from the plist):
#   EMAIL_CLIPPER_INBOX  — directory to scan (default: ~/Obsidian Inbox)
#   EMAIL_CLIPPER_VAULT  — Reading List directory (default: ~/Obsidian/vault/Reading List)
#   EMAIL_CLIPPER_BIN    — path to the email-clipper executable
#                          (default: ~/Library/Application Support/email-clipper/venv/bin/email-clipper)

set -u

INBOX="${EMAIL_CLIPPER_INBOX:-$HOME/Obsidian Inbox}"
VAULT="${EMAIL_CLIPPER_VAULT:-$HOME/Obsidian/vault/Reading List}"
BIN="${EMAIL_CLIPPER_BIN:-$HOME/Library/Application Support/email-clipper/venv/bin/email-clipper}"
LOG="$HOME/Library/Logs/email-clipper.log"

mkdir -p "$INBOX" "$INBOX/processed" "$INBOX/failed" "$(dirname "$LOG")"

shopt -s nullglob
for eml in "$INBOX"/*.eml; do
    name="$(basename "$eml")"
    if "$BIN" "$eml" --vault "$VAULT" >>"$LOG" 2>&1; then
        mv -f "$eml" "$INBOX/processed/$name"
        echo "[$(date -u +%FT%TZ)] OK   $name" >>"$LOG"
    else
        mv -f "$eml" "$INBOX/failed/$name"
        echo "[$(date -u +%FT%TZ)] FAIL $name" >>"$LOG"
    fi
done
