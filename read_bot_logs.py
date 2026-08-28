import os

for fn in ['bot2-out.log', 'bot2-err.log', 'bot1-out.log', 'bot1-err.log']:
  p = rf'C:\apps\bot-keo-nhom-bcr-main\logs\{fn}'
  print(f'=== {fn} ===')
  if os.path.exists(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
      lines = f.readlines()
      for l in lines[-12:]:
        print(l.strip().encode('ascii', errors='replace').decode('ascii'))
  else:
    print('Not found')
  print()
