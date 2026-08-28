import asyncio
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 32866514
API_HASH = '64436fe83185c956bece789a6f3253b8'
PHONE = '+84776956765'
TWOFA = 'RUBY2E'
PHONE_CODE_HASH = '85641dcd09868ed265'
CODE = sys.argv[1] if len(sys.argv) > 1 else ''

async def main():
    if not CODE:
        print("MISSING_CODE")
        return

    client = TelegramClient('user_session_84776956765', API_ID, API_HASH)
    await client.connect()
    try:
        print(f'Signing in with code {CODE} and hash {PHONE_CODE_HASH}...', flush=True)
        try:
            await client.sign_in(PHONE, code=CODE, phone_code_hash=PHONE_CODE_HASH)
        except SessionPasswordNeededError:
            print('Entering 2FA password...', flush=True)
            await client.sign_in(password=TWOFA)
            
        me = await client.get_me()
        print(f'SUCCESS_AUTHORIZED: {me.first_name} (@{me.username})', flush=True)
    except Exception as e:
        print(f'SIGN_IN_ERROR: {e}', flush=True)
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
