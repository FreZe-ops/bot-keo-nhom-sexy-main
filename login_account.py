import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

phone = '+84365618453'
api_id = 30590012
api_hash = '66d4b8c135ab325038bda084a5453fe7'
twofa = 'HAIYEN123@'
code = '39805'
phone_code_hash = '645f49069367c28325'
session_name = f'tele_session_{phone.replace("+", "")}'

client = TelegramClient(session_name, api_id, api_hash)

async def signin():
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        print("LOGIN_SUCCESS_NO_2FA")
    except SessionPasswordNeededError:
        await client.sign_in(password=twofa)
        print("LOGIN_SUCCESS_WITH_2FA")
    except Exception as e:
        print(f"LOGIN_ERROR: {e}")
        # Try sign_in with just code if phone_code_hash not needed
        try:
            await client.sign_in(phone=phone, code=code)
            print("LOGIN_SUCCESS_RETRY")
        except SessionPasswordNeededError:
            await client.sign_in(password=twofa)
            print("LOGIN_SUCCESS_RETRY_2FA")
        except Exception as e2:
            print(f"LOGIN_ERROR_2: {e2}")
    
    me = await client.get_me()
    print(f"AUTHENTICATED AS: {me.first_name} (@{me.username}) ID={me.id}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(signin())
