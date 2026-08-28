import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from bot_forward_runner import TelegramForwardBot, get_account_by_id

async def test():
    acc = get_account_by_id('bot_forward_6')
    bot = TelegramForwardBot(acc)
    ok = await bot.connect_and_login(interactive=False)
    if not ok:
        print("LOGIN FAILED")
        return
    source = await bot.resolve_entity(bot.source_username)
    messages = []
    async for m in bot.client.iter_messages(source, limit=20):
        messages.append(m)
    messages.sort(key=lambda x: x.id)
    print(f"Fetched {len(messages)} messages from @{bot.source_username}")
    await bot.execute_round(messages)
    await bot.client.disconnect()

if __name__ == '__main__':
    asyncio.run(test())
