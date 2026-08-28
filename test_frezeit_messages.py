import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
digits = ''.join(c for c in phone if c.isdigit())
session_name = f'user_session_{digits}_ns1'

async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    user = await client.get_entity('frezeit')
    msgs = []
    async for m in client.iter_messages(user, limit=20):
        msgs.append(m)
    msgs.sort(key=lambda x: x.id)
    print(f"=== FOUND {len(msgs)} MESSAGES FROM @frezeit ===")
    for i, m in enumerate(msgs):
        txt = (m.text or m.message or '[MEDIA]').replace('\n', ' ')[:50]
        print(f"[{i}] ID={m.id} | {txt}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
