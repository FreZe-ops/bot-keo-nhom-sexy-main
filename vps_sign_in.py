import paramiko
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

OTP_CODE = sys.argv[1] if len(sys.argv) > 1 else '94937'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

script = f"""
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 32866514
API_HASH = '64436fe83185c956bece789a6f3253b8'
PHONE = '+84776956765'
TWOFA = 'RUBY2E'
CODE = '{OTP_CODE}'

async def main():
    client = TelegramClient('user_session_84776956765', API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f'ALREADY_AUTHORIZED: {{me.first_name}} (@{{me.username}})')
        await client.disconnect()
        return

    try:
        # Check if code sign in works directly or request new
        print('Signing in with code...')
        try:
            await client.sign_in(PHONE, code=CODE)
        except SessionPasswordNeededError:
            print('Entering 2FA...')
            await client.sign_in(password=TWOFA)
            
        me = await client.get_me()
        print(f'SUCCESS_AUTHORIZED: {{me.first_name}} (@{{me.username}})')
    except Exception as e:
        print(f'SIGN_IN_ERROR: {{e}}')
        # If hash missing, request new code
        print('Requesting fresh code...')
        sent = await client.send_code_request(PHONE)
        print('NEW_CODE_SENT')
    finally:
        await client.disconnect()

asyncio.run(main())
"""

# Chạy trực tiếp script python trên VPS
stdin, stdout, stderr = ssh.exec_command(f'cd /d C:\\apps\\bot-keo-nhom-bcr-main & C:\\tools\\python\\python.exe -c "{script}"')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== VPS SIGN IN OUTPUT ===")
print(out)
if err.strip():
    print(f"[STDERR]: {err}")

ssh.close()
