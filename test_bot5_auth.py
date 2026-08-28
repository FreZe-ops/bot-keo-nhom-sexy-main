import asyncio
from telethon import TelegramClient

async def test_bot5():
    api_id = 30590012
    api_hash = "66d4b8c135ab325038bda084a5453fe7"
    session_name = "user_session_84365618453"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    auth = await client.is_user_authorized()
    print("is_user_authorized:", auth)
    if auth:
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username}) ID={me.id}")
    else:
        print("NOT AUTHORIZED - Session invalid or logged out!")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(test_bot5())
