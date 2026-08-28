import os

for fname in ['bot1-out.log', 'bot2-out.log', 'bot3-out.log', 'bot4-out.log', 'bot2-err.log', 'forward_bot_out.log', 'forward_bot_err.log', 'watchdog_err.log']:
    p = os.path.join(r'C:\apps\bot-keo-nhom-bcr-main', fname)
    print(f"\n==================== {fname} (size={os.path.getsize(p) if os.path.exists(p) else 0}) ====================")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        try:
            with open(p, 'rb') as f:
                f.seek(max(0, os.path.getsize(p) - 3000))
                content = f.read().decode('utf-8', errors='replace')
                lines = content.strip().split('\n')
                for l in lines[-15:]:
                    print(l)
        except Exception as ex:
            print("ERR:", ex)
