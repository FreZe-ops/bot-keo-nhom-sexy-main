import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

def run(cmd):
    print(f"\n>>> [EXEC] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print(f"[STDERR]: {err}")
    return out

# 1. Cài đặt Service Windows BCR-forward-bot qua NSSM (chạy 24/7 tự khởi động cùng VPS)
run(r'C:\tools\nssm\nssm.exe stop BCR-forward-bot')
run(r'C:\tools\nssm\nssm.exe remove BCR-forward-bot confirm')
run(r'C:\tools\nssm\nssm.exe install BCR-forward-bot "C:\tools\python\python.exe" "C:\apps\bot-keo-nhom-bcr-main\bot_forward_runner.py --all"')
run(r'C:\tools\nssm\nssm.exe set BCR-forward-bot AppDirectory "C:\apps\bot-keo-nhom-bcr-main"')
run(r'C:\tools\nssm\nssm.exe set BCR-forward-bot AppStdout "C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log"')
run(r'C:\tools\nssm\nssm.exe set BCR-forward-bot AppStderr "C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_err.log"')
run(r'C:\tools\nssm\nssm.exe set BCR-forward-bot AppRestartDelay 5000')
run(r'C:\tools\nssm\nssm.exe start BCR-forward-bot')

# 2. Khởi động lại toàn bộ các session cào và bot cũ
print("\n=== RESTARTING ALL BCR SERVICES ===")
for s in ['BCR-server', 'BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4', 'BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4']:
    run(f'net stop {s} & net start {s}')

# 3. Kiểm tra trạng thái toàn bộ dịch vụ
print("\n=== VERIFYING SERVICES STATUS ===")
run(r'sc query BCR-forward-bot')
run(r'sc query BCR-server')
run(r'sc query BCR-session1')
run(r'sc query BCR-bot1')

ssh.close()
