import os, time

root = r'C:\apps\bot-keo-nhom-bcr-main'
for f in os.listdir(root):
    if f.endswith('.log'):
        p = os.path.join(root, f)
        mtime = time.ctime(os.path.getmtime(p))
        size = os.path.getsize(p)
        print(f"{f:30} size={size:10} modified={mtime}")
