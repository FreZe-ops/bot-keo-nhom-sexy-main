import asyncio
import json
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

PHONE = "+84878377698"
API_ID = 30590012
API_HASH = "66d4b8c135ab325038bda084a5453fe7"
SESSION_NAME = "user_session_84878377698"
HASH_FILE = "C:/apps/bot-keo-nhom-bcr-main/otp_hash_bot2.json"

async def sign_in_with_code(code, twofa_pwd=None):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    phone_code_hash = data["phone_code_hash"]

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    try:
        await client.sign_in(phone=PHONE, code=code, phone_code_hash=phone_code_hash)
        print("SIGN_IN_SUCCESS")
    except SessionPasswordNeededError:
        if twofa_pwd:
            await client.sign_in(password=twofa_pwd)
            print("2FA_SIGN_IN_SUCCESS")
        else:
            print("NEEDS_2FA")
            await client.disconnect()
            return

    me = await client.get_me()
    print(f"USER: {me.first_name} (@{me.username}) ID={me.id}")
    print("=== LISTING GROUPS / DIALOGS ===")
    async for d in client.iter_dialogs(limit=30):
        if d.is_group or d.is_channel:
            print(f"GROUP: id={d.id} title='{d.title}'")

    await client.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sign_in_bot2.py <OTP_CODE> [2FA_PASSWORD]")
        sys.exit(1)
    code = sys.argv[1].strip()
    twofa = sys.argv[2].strip() if len(sys.argv) > 2 else None
    asyncio.run(sign_in_with_code(code, twofa))
