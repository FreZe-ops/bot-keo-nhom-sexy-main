import glob
import json
import os
import time
import urllib.request

print("=== BẮT ĐẦU THEO DÕI LIVE CAPTURE & SESSION (60S INTERVAL) ===")
sdir = r'C:\apps\bot-keo-nhom-bcr-main\public\screenshots'

start_t = time.time()
last_seen_files = set()
if os.path.exists(sdir):
  last_seen_files = set(os.listdir(sdir))

print(f"Ảnh hiện có: {len(last_seen_files)} files")

for sample in range(6):
  time.sleep(15)
  elapsed = int(time.time() - start_t)

  # Check active tables
  active_summary = {}
  for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
    try:
      url = f'http://127.0.0.1:3201/api/get-active-table?nameService={ns}'
      with urllib.request.urlopen(url, timeout=2.5) as r:
        d = json.loads(r.read().decode('utf-8'))
        active_summary[ns] = d.get('activeTable') or 'None'
    except Exception as e:
      active_summary[ns] = f'Err({e})'

  # Check new screenshots
  new_shots = []
  if os.path.exists(sdir):
    cur_files = set(os.listdir(sdir))
    diff = cur_files - last_seen_files
    for f in diff:
      fp = os.path.join(sdir, f)
      mtime = os.path.getmtime(fp)
      new_shots.append((f, time.time() - mtime))
    last_seen_files = cur_files

  print(f"\n[{elapsed:02d}s] Active Tables: {active_summary}")
  if new_shots:
    for nf, age in new_shots:
      print(f"  📸 [MỚI CHỤP]: {nf} (cách đây {age:.1f}s)")
  else:
    print("  ... Chưa có ván mới trong 15s qua (đang đợi dealer chia/lật bài)")

print("\n=== KẾT THÚC THEO DÕI ===")
