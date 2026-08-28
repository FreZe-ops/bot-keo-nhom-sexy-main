import asyncio
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 32866514
API_HASH = '64436fe83185c956bece789a6f3253b8'
PHONE = '+84776956765'
TWOFA = 'RUBY2E'
CODE = sys.argv[1] if len(sys.argv) > 1 else '94937'

async def main():
    client = TelegramClient('user_session_84776956765', API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f'ALREADY_AUTHORIZED: {me.first_name} (@{me.username})', flush=True)
        await client.disconnect()
        return

    try:
        print(f'Signing in with code {CODE}...', flush=True)
        try:
            await client.sign_in(PHONE, code=CODE)
        except SessionPasswordNeededError:
            print('Entering 2FA...', flush=True)
            await client.sign_in(password=TWOFA)
            
        me = await client.get_me()
        print(f'SUCCESS_AUTHORIZED: {me.first_name} (@{me.username})', flush=True)
    except Exception as e:
        print(f'SIGN_IN_ERROR: {e}', flush=True)
        print('Requesting fresh code...', flush=True)
        sent = await client.send_code_request(PHONE)
        print(f'NEW_CODE_SENT: hash={sent.phone_code_hash}', flush=True)
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
