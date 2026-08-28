import asyncio
import json
from telethon import TelegramClient

async def request_otp():
    api_id = 30590012
    api_hash = "66d4b8c135ab325038bda084a5453fe7"
    session_name = "user_session_84365618453"
    phone = "+84365618453"
    
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    res = await client.send_code_request(phone)
    print("PHONE_CODE_HASH:", res.phone_code_hash)
    with open('bot5_hash.json', 'w') as f:
        json.dump({'hash': res.phone_code_hash}, f)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(request_otp())
