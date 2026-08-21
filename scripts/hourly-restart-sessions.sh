#!/usr/bin/env bash
# Restart all Playwright sessions every hour, staggered so 4 nicks
# do not hit the lobby at the same time.
set -u

export PATH="/usr/local/bin:/usr/bin:/bin:${PATH:-}"
export PM2_HOME="${PM2_HOME:-/root/.pm2}"

LOCK="/var/lock/hourly-restart-sessions.lock"
LOG="/var/log/session-hourly-restart.log"
STAGGER_SEC="${STAGGER_SEC:-75}"
SESSIONS=(session_sexy_1 session_sexy_2 session_sexy_3 session_sexy_4)

mkdir -p "$(dirname "$LOG")" /var/lock 2>/dev/null || true

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] skip — previous hourly restart still running" >>"$LOG"
  exit 0
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

if ! command -v pm2 >/dev/null 2>&1; then
  log "pm2 not in PATH — abort"
  exit 1
fi

log "hourly restart start (stagger=${STAGGER_SEC}s)"
last_idx=$((${#SESSIONS[@]} - 1))
for i in "${!SESSIONS[@]}"; do
  name="${SESSIONS[$i]}"
  if pm2 describe "$name" >/dev/null 2>&1; then
    log "pm2 restart $name"
    pm2 restart "$name" --update-env >/dev/null || log "WARN restart failed: $name"
  else
    log "skip $name — not in pm2"
  fi
  if [[ "$i" -lt "$last_idx" ]]; then
    sleep "$STAGGER_SEC"
  fi
done
log "hourly restart done"
