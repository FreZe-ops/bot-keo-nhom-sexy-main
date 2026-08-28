import asyncio
import json
import os
import glob
from telethon import TelegramClient

async def request_fresh_otp():
    api_id = 33296584
    api_hash = "02a20fdfd8678cbc8cef9b0dfccaea90"
    session_name = r"C:\apps\bot-keo-nhom-bcr-main\user_session_84995242731"
    phone = "+84995242731"
    
    # Remove stale session files to force Telegram to start a clean new handshake
    for f in glob.glob(session_name + '*'):
        try:
            os.remove(f)
        except Exception:
            pass
            
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    res = await client.send_code_request(phone)
    print("NEW_PHONE_CODE_HASH:", res.phone_code_hash)
    print("CODE_TYPE:", type(res.type).__name__)
    with open(r'C:\apps\bot-keo-nhom-bcr-main\new_account_hash.json', 'w') as f:
        json.dump({'hash': res.phone_code_hash, 'phone': phone, 'api_id': api_id, 'api_hash': api_hash}, f)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(request_fresh_otp())
