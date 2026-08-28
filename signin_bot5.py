import asyncio
import json
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError

async def sign_in():
    api_id = 30590012
    api_hash = "66d4b8c135ab325038bda084a5453fe7"
    session_name = "user_session_84365618453"
    phone = "+84365618453"
    twofa = "HAIYEN123@"
    code = "89732"
    
    with open('bot5_hash.json', 'r') as f:
        data = json.load(f)
        phone_code_hash = data['hash']
        
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        print("SIGNIN_SUCCESS")
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username}) ID={me.id}")
    except SessionPasswordNeededError:
        print("NEED_2FA")
        await client.sign_in(password=twofa)
        print("SIGNIN_2FA_SUCCESS")
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username}) ID={me.id}")
    except PhoneCodeExpiredError:
        print("CODE_EXPIRED")
    except PhoneCodeInvalidError:
        print("CODE_INVALID")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(sign_in())
