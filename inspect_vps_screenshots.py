import os
import time

sdir = r'C:\apps\bot-keo-nhom-bcr-main\public\screenshots'
if os.path.exists(sdir):
    files = [os.path.join(sdir, f) for f in os.listdir(sdir) if os.path.isfile(os.path.join(sdir, f))]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    print(f"=== SCREENSHOTS (Total {len(files)}) ===")
    for f in files[:10]:
        age = time.time() - os.path.getmtime(f)
        print(f"{os.path.basename(f)} | age: {age:.1f}s ago")
else:
    print("No screenshots dir")
