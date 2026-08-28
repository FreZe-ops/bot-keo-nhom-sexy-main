import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot_forward_runner import BotForwardRunner, load_accounts_config

async def test_run():
  accounts = load_accounts_config()
  acc = next((a for a in accounts if a['id'] == 'bot_forward_5'), None)
  if not acc:
    print('Account bot_forward_5 not found')
    return

  runner = BotForwardRunner(acc)
  ok = await runner.connect_and_login(interactive=False)
  print(f'Login status: {ok}')
  if ok:
    print('Testing execute_round for bot_forward_5...')
    await runner.execute_round()
    await runner.client.disconnect()


if __name__ == '__main__':
  asyncio.run(test_run())
