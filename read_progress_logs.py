import os

log_dir = r'C:\apps\bot-keo-nhom-bcr-main\logs'
for fn in os.listdir(log_dir):
  fp = os.path.join(log_dir, fn)
  if os.path.isfile(fp):
    print(f'=== {fn} ===')
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
      lines = f.readlines()
      for l in lines[-12:]:
        print(l.strip().encode('ascii', errors='replace').decode('ascii'))
    print()
