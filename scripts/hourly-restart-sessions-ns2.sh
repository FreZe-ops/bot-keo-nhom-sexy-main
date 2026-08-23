#!/usr/bin/env bash
# Restart single session hourly
set -u
export PATH="/usr/local/bin:/usr/bin:/bin:${PATH:-}"
export PM2_HOME="${PM2_HOME:-/root/.pm2}"
LOCK="/var/lock/hourly-restart-sessions.lock"
LOG="/var/log/session-hourly-restart.log"
mkdir -p "$(dirname "$LOG")" /var/lock 2>/dev/null || true
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] skip — previous still running" >>"$LOG"
  exit 0
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] pm2 restart session_sexy_2" >>"$LOG"
pm2 restart session_sexy_2 --update-env >>"$LOG" 2>&1 || true
echo "[$(date '+%Y-%m-%d %H:%M:%S')] done" >>"$LOG"
