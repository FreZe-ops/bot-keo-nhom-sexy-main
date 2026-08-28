import asyncio
import json
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError

async def sign_in_with_code(code_str):
    code_str = code_str.strip()
    api_id = 33296584
    api_hash = "02a20fdfd8678cbc8cef9b0dfccaea90"
    session_name = r"C:\apps\bot-keo-nhom-bcr-main\user_session_84995242731"
    phone = "+84995242731"
    twofa = "2012"
    
    with open(r'C:\apps\bot-keo-nhom-bcr-main\new_account_hash.json', 'r') as f:
        data = json.load(f)
        phone_code_hash = data['hash']
        
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code_str, phone_code_hash=phone_code_hash)
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
    if len(sys.argv) > 1:
        asyncio.run(sign_in_with_code(sys.argv[1]))
    else:
        print("USAGE: python interactive_signin.py <code_5_digits>")
