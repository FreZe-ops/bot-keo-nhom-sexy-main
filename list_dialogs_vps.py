import asyncio
import sys
from telethon import TelegramClient

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PHONE = "+84878377698"
API_ID = 30590012
API_HASH = "66d4b8c135ab325038bda084a5453fe7"
SESSION_NAME = "user_session_84878377698"

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("NOT_AUTHORIZED")
        return

    me = await client.get_me()
    print(f"USER_INFO: name='{me.first_name} {me.last_name or ''}' username='@{me.username}' id={me.id}")
    print("\n=== LIST OF GROUPS / CHANNELS ===")
    async for d in client.iter_dialogs(limit=50):
        if d.is_group or d.is_channel:
            print(f"GROUP: id={d.id} title='{d.title}'")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
