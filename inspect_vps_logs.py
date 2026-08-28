import os
import sys

def print_tail(filepath, n_lines=40):
    print(f"\n==================== TAIL OF {os.path.basename(filepath)} ====================")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            for l in lines[-n_lines:]:
                sys.stdout.buffer.write((l.rstrip() + '\n').encode('utf-8'))
    except Exception as e:
        print("Error reading:", e)

for lf in [
    r'C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log',
    r'C:\apps\bot-keo-nhom-bcr-main\logs\server-out.log',
    r'C:\apps\bot-keo-nhom-bcr-main\logs\session1-out.log',
    r'C:\apps\bot-keo-nhom-bcr-main\logs\session2-out.log',
    r'C:\apps\bot-keo-nhom-bcr-main\logs\session3-out.log',
    r'C:\apps\bot-keo-nhom-bcr-main\logs\session4-out.log',
]:
    print_tail(lf, 35)
