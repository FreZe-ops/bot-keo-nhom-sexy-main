#!/bin/bash
set -e
cd /var/www/bot-keo-nhom-bcr/bot-keo-nhom-bcr-main
pm2 delete server_sexy session_sexy_1 session_sexy_2 session_sexy_3 session_sexy_4 session_sexy_5 bot_sexy_1 bot_sexy_2 bot_sexy_3 bot_sexy_4 bot_sexy_5 >/dev/null 2>&1 || true
cp -f ecosystem.config.production.js ecosystem.config.js
pm2 start ecosystem.config.js
pm2 save
pm2 ls
