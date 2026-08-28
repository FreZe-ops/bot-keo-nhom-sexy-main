import asyncio
from telethon import TelegramClient

async def test_auth():
    api_id = 33296584
    api_hash = "02a20fdfd8678cbc8cef9b0dfccaea90"
    session_name = r"C:\apps\bot-keo-nhom-bcr-main\user_session_84995242731"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    auth = await client.is_user_authorized()
    print("IS_AUTHORIZED:", auth)
    if auth:
        me = await client.get_me()
        print(f"Logged in successfully as: {me.first_name} (@{me.username}) ID={me.id}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(test_auth())
