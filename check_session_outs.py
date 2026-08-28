import os

for lf in ['session1-out.log', 'session2-out.log', 'session3-out.log', 'session4-out.log']:
  p = rf'C:\apps\bot-keo-nhom-bcr-main\logs\{lf}'
  print(f'=== {lf} ===')
  if os.path.exists(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
      lines = f.readlines()
      for l in lines[-10:]:
        print(l.strip().encode('ascii', errors='replace').decode('ascii'))
  else:
    print('File not found')
  print()
