#!/bin/bash
cd /var/www/bot-keo-nhom-bcr/bot-keo-nhom-bcr-main
export ACCOUNT_INDEX=2
export PREFERRED_TABLE=C03
export SKIP_BOOT_DELAY=1
export DOTENV_CONFIG_PATH=/var/www/bot-keo-nhom-bcr/bot-keo-nhom-bcr-main/.env
exec node --max-old-space-size=1536 -r dotenv/config servicePuppeteer/session.js
