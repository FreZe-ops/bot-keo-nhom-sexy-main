import glob
import json
import os
import subprocess
import time
import urllib.request

print("=== 1. CHECKING SCREENSHOTS (LATEST 15) ===")
sdir = r'C:\apps\bot-keo-nhom-bcr-main\public\screenshots'
if os.path.exists(sdir):
  files = [
      os.path.join(sdir, f)
      for f in os.listdir(sdir)
      if os.path.isfile(os.path.join(sdir, f))
  ]
  files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
  for f in files[:15]:
    age_m = (time.time() - os.path.getmtime(f)) / 60.0
    print(f'{os.path.basename(f)} | {age_m:.1f} mins ago')

print("\n=== 2. CHECKING NSSM SERVICES ===")
for s in [
    'BCR-server',
    'BCR-session1',
    'BCR-session2',
    'BCR-session3',
    'BCR-session4',
    'BCR-forward-bot',
]:
  try:
    cmd = rf'C:\tools\nssm\nssm-2.24\win64\nssm.exe status {s}'
    res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    print(f'{s}: {res}')
  except Exception as e:
    print(f'{s}: Error {e}')

print("\n=== 3. CHECKING SERVER /api/get-active-table ===")
for ns in ['NS1', 'NS2', 'NS3', 'NS4', 'NS5']:
  try:
    url = f'http://127.0.0.1:3201/api/get-active-table?nameService={ns}'
    with urllib.request.urlopen(url, timeout=3) as r:
      d = json.loads(r.read().decode('utf-8'))
      print(f'[{ns}] {d}')
  except Exception as e:
    print(f'[{ns}] Error: {e}')

print("\n=== 4. CHECKING SESSION LOGS (TAIL 10 LINES EACH) ===")
log_dir = r'C:\apps\bot-keo-nhom-bcr-main\logs'
if os.path.exists(log_dir):
  for lf in os.listdir(log_dir):
    lp = os.path.join(log_dir, lf)
    if os.path.isfile(lp) and (
        'progress' in lf or 'sexy' in lf or 'server' in lf
    ):
      print(f'--- LOG: {lf} ---')
      try:
        with open(lp, 'r', encoding='utf-8', errors='replace') as fp:
          lines = fp.readlines()
          for l in lines[-8:]:
            print(l.strip())
      except Exception as ex:
        print('Error reading log:', ex)
