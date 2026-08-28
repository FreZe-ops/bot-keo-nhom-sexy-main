import os

root = r'C:\apps'
for r, d, files in os.walk(root):
    for f in files:
        if f.endswith('.log'):
            p = os.path.join(r, f)
            print(f"{p} ({os.path.getsize(p)} bytes)")
