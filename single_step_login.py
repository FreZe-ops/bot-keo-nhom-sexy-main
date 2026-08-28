import asyncio
import json
import os
import glob
import sys
from telethon import TelegramClient

async def generate_and_save_request():
    api_id = 33296584
    api_hash = "02a20fdfd8678cbc8cef9b0dfccaea90"
    session_name = r"C:\apps\bot-keo-nhom-bcr-main\user_session_84995242731"
    phone = "+84995242731"
    
    for f in glob.glob(session_name + '*'):
        try:
            os.remove(f)
        except Exception:
            pass
            
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    res = await client.send_code_request(phone)
    print("PHONE_CODE_HASH:", res.phone_code_hash)
    with open(r'C:\apps\bot-keo-nhom-bcr-main\current_login_hash.json', 'w') as f:
        json.dump({'hash': res.phone_code_hash, 'phone': phone}, f)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(generate_and_save_request())
