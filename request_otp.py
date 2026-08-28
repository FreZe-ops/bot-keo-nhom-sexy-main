import asyncio
from telethon import TelegramClient

phone = '+84365618453'
api_id = 30590012
api_hash = '66d4b8c135ab325038bda084a5453fe7'
session_name = f'tele_session_{phone.replace("+", "")}'

client = TelegramClient(session_name, api_id, api_hash)

async def req_code():
    await client.connect()
    if not await client.is_user_authorized():
        res = await client.send_code_request(phone)
        print(f"OTP_SENT_SUCCESS phone_code_hash={res.phone_code_hash}")
    else:
        print("ALREADY_AUTHORIZED")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(req_code())
