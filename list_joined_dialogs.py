import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
digits = ''.join(c for c in phone if c.isdigit())
session_name = f'user_session_{digits}_ns1'

async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print("Not logged in!")
        return
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username}) ID={me.id}")
    print("\n=== DANH SÁCH NHÓM / CHANNEL TÀI KHOẢN ĐÃ THAM GIA ===")
    count = 0
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, (Channel, Chat)):
            count += 1
            print(f"[{count}] Tên: '{dialog.name}' | ID: {dialog.id} | Username: @{getattr(entity, 'username', 'None')} | Type: {type(entity).__name__}")
        elif isinstance(entity, User) and getattr(entity, 'username', '') == 'frezeit':
            print(f"[SOURCE] Nguồn frezeit ID={entity.id}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
