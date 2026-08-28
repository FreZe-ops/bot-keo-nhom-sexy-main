import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

root = r'C:\apps\bot-keo-nhom-bcr-main\logs'
for fname in ['bot1-out.log', 'bot2-out.log', 'bot3-out.log', 'bot4-out.log', 'forward_bot_out.log', 'watchdog_err.log']:
    p = os.path.join(root, fname)
    if os.path.exists(p):
        print(f"\n==================== {fname} ====================")
        try:
            with open(p, 'rb') as f:
                f.seek(max(0, os.path.getsize(p) - 4000))
                content = f.read().decode('utf-8', errors='replace')
                lines = [l for l in content.strip().split('\n') if l.strip()]
                for l in lines[-12:]:
                    print(l)
        except Exception as ex:
            print("ERR:", ex)
