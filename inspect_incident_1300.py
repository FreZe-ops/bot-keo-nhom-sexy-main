import os

for lf in ['session3-out.log', 'session3-err.log', 'bot3-out.log', 'bot3-err.log', 'bot.log', 'tele_out.log']:
  p = rf'C:\apps\bot-keo-nhom-bcr-main\logs\{lf}'
  print(f'=== {lf} ===')
  if os.path.exists(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
      lines = f.readlines()
      for l in lines[-20:]:
        print(l.strip().encode('ascii', errors='replace').decode('ascii'))
  else:
    print('Not found')
  print()
