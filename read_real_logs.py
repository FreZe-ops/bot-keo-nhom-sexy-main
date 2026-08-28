import os

root = r'C:\apps\bot-keo-nhom-bcr-main\logs'
for fname in ['bot1-out.log', 'bot2-out.log', 'bot3-out.log', 'bot4-out.log', 'bot2-err.log', 'forward_bot_out.log', 'session1-out.log', 'session2-out.log', 'session3-out.log', 'session4-out.log']:
    p = os.path.join(root, fname)
    if os.path.exists(p):
        print(f"\n==================== {fname} (size={os.path.getsize(p)}) ====================")
        try:
            with open(p, 'rb') as f:
                f.seek(max(0, os.path.getsize(p) - 2000))
                content = f.read().decode('utf-8', errors='replace')
                lines = content.strip().split('\n')
                for l in lines[-10:]:
                    print(l)
        except Exception as ex:
            print("ERR:", ex)
