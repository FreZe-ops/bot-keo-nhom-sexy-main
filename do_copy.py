import shutil
import os

src = r'C:\apps\bot-keo-nhom-bcr-main\tele_session_84365618453.session'
dst = r'C:\apps\bot-keo-nhom-bcr-main\user_session_84365618453.session'

if os.path.exists(src):
    shutil.copyfile(src, dst)
    print(f"COPIED {src} -> {dst} (Size: {os.path.getsize(dst)} bytes)")
else:
    print(f"SOURCE NOT FOUND: {src}")
