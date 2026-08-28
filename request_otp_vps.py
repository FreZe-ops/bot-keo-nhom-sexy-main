import asyncio
import json
import os
import sys
from telethon import TelegramClient

PHONE = "+84878377698"
API_ID = 30590012
API_HASH = "66d4b8c135ab325038bda084a5453fe7"
SESSION_NAME = "user_session_84878377698"
HASH_FILE = "C:/apps/bot-keo-nhom-bcr-main/otp_hash_bot2.json"

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"ALREADY_AUTHORIZED: {me.first_name} (@{me.username}) ID={me.id}")
        await client.disconnect()
        return

    print(f"Sending OTP request to {PHONE}...")
    sent = await client.send_code_request(PHONE)
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "phone": PHONE,
            "phone_code_hash": sent.phone_code_hash
        }, f)
    print(f"OTP_SENT_SUCCESS: phone_code_hash={sent.phone_code_hash}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
