#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq curl git ca-certificates gnupg build-essential python3-venv python3-pip unzip tar

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi
node -v
npm -v
npm i -g pm2

if ! command -v mongod >/dev/null 2>&1; then
  curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
  echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
    > /etc/apt/sources.list.d/mongodb-org-7.0.list
  apt-get update -qq
  apt-get install -y -qq mongodb-org
fi
systemctl enable mongod >/dev/null 2>&1 || true
systemctl start mongod || true
sleep 2
mongosh --quiet --eval 'db.runCommand({ping:1})' || true

mkdir -p /var/www/bot-keo-nhom-bcr/bot-keo-nhom-bcr-main
echo BOOTSTRAP_OK
