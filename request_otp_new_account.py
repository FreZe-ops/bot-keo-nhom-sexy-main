import asyncio
import json
from telethon import TelegramClient

async def request_otp():
    api_id = 33296584
    api_hash = "02a20fdfd8678cbc8cef9b0dfccaea90"
    session_name = "user_session_84995242731"
    phone = "+84995242731"
    
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    res = await client.send_code_request(phone)
    print("PHONE_CODE_HASH:", res.phone_code_hash)
    with open('new_account_hash.json', 'w') as f:
        json.dump({'hash': res.phone_code_hash, 'phone': phone, 'api_id': api_id, 'api_hash': api_hash}, f)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(request_otp())
