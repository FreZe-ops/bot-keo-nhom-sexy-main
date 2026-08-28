import os
import time
import glob

dirs = [r'C:\apps\bot-keo-nhom-bcr-main\public\screenshots', r'C:\apps\bot-keo-nhom-bcr-main\screenshots']
all_files = []
for d in dirs:
    if os.path.exists(d):
        for f in os.listdir(d):
            if f.endswith('.png'):
                fp = os.path.join(d, f)
                all_files.append((fp, os.path.getmtime(fp), os.path.getsize(fp)))

all_files.sort(key=lambda x: x[1], reverse=True)
print(f'Total screenshots: {len(all_files)}')
print('Latest 30 screenshots:')
for fp, mt, sz in all_files[:30]:
    tstr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mt))
    print(f'  {tstr} | {sz} bytes | {os.path.basename(fp)}')
