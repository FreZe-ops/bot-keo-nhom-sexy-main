import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

p = r'C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log'
if os.path.exists(p):
    with open(p, 'rb') as f:
        content = f.read().decode('utf-8', errors='replace')
    lines = content.split('\n')
    print(f"Total lines in log: {len(lines)}")
    matches = []
    for l in lines:
        if any(k in l for k in ['KHOI DONG', 'KHỞI ĐỘNG', 'Lịch chạy', 'Dang nhap', 'Đăng nhập', 'Trâm Anh', 'MINH', 'Hải Yến', 'Hai Yen', 'Bắt đầu ca', 'HOÀN THÀNH', 'ERROR', 'WARN']):
            matches.append(l)
    print(f"Matched lines: {len(matches)}")
    for m in matches[-40:]:
        print(m)
else:
    print(f"File not found: {p}")
