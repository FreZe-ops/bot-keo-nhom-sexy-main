import asyncio
import json
import os
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

SESSION_DIR = r'C:\apps\bot-keo-nhom-bcr-main'
PHONE = '+84566123980'
API_ID = 18214111
API_HASH = '2aa34f73907e52b2a05147878356e5e9'
SESSION_NAME = os.path.join(SESSION_DIR, 'user_session_84566123980')

async def send_otp():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"ALREADY_LOGGED_IN: {me.first_name} (@{me.username})")
        await client.disconnect()
        return
    
    print(f"Sending OTP to {PHONE}...")
    sent = await client.send_code_request(PHONE)
    with open(os.path.join(SESSION_DIR, 'otp_bot3_hash.json'), 'w') as f:
        json.dump({'phone_code_hash': sent.phone_code_hash}, f)
    print("OTP_SENT_SUCCESSFULLY")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(send_otp())
