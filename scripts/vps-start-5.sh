#!/bin/bash
set -e
cd /var/www/bot-keo-nhom-bcr/bot-keo-nhom-bcr-main
pm2 delete ecosystem.config.production >/dev/null 2>&1 || true
pm2 delete server_sexy session_sexy_1 session_sexy_2 session_sexy_3 session_sexy_4 session_sexy_5 bot_sexy_1 bot_sexy_2 bot_sexy_3 bot_sexy_4 bot_sexy_5 >/dev/null 2>&1 || true
node -e 'const e=require("./ecosystem.config.production.js"); console.log("APPS", e.apps.map(a=>a.name+(a.env&&a.env.TARGET_TABLE?("="+a.env.TARGET_TABLE):"")).join(" | "));'
pm2 start ecosystem.config.production.js
pm2 save
pm2 ls
