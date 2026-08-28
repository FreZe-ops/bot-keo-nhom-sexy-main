import asyncio
import json
import os
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

SESSION_DIR = r'C:\apps\bot-keo-nhom-bcr-main'
PHONE = '+84566123980'
API_ID = 18214111
API_HASH = '2aa34f73907e52b2a05147878356e5e9'
SESSION_NAME = os.path.join(SESSION_DIR, 'user_session_84566123980')

async def complete_login(otp_code, twofa_pwd=None):
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"SUCCESS: {me.first_name} (@{me.username})")
        await client.disconnect()
        return
    
    hash_file = os.path.join(SESSION_DIR, 'otp_bot3_hash.json')
    if not os.path.exists(hash_file):
        print("ERROR: No phone_code_hash found. Please request OTP first.")
        await client.disconnect()
        return
        
    with open(hash_file, 'r') as f:
        data = json.load(f)
    phone_code_hash = data['phone_code_hash']
    
    try:
        await client.sign_in(phone=PHONE, code=otp_code, phone_code_hash=phone_code_hash)
        me = await client.get_me()
        print(f"SUCCESS: {me.first_name} (@{me.username})")
    except SessionPasswordNeededError:
        if twofa_pwd:
            await client.sign_in(password=twofa_pwd)
            me = await client.get_me()
            print(f"SUCCESS_2FA: {me.first_name} (@{me.username})")
        else:
            print("NEED_2FA")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    otp = sys.argv[1] if len(sys.argv) > 1 else ''
    pwd = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(complete_login(otp, pwd))
