import paramiko
import sys
import time

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
    if out.strip():
        print(out)
    if err.strip():
        print(f"[STDERR]: {err}")
    return out

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

# 1. Cài đặt Service BCR-forward-bot
print("=== 1. INSTALLING BCR-forward-bot SERVICE ===")
run(f'{NSSM} stop BCR-forward-bot')
run(f'{NSSM} remove BCR-forward-bot confirm')
run(f'{NSSM} install BCR-forward-bot "C:\\tools\\python\\python.exe" "bot_forward_runner.py --all"')
run(f'{NSSM} set BCR-forward-bot AppDirectory "C:\\apps\\bot-keo-nhom-bcr-main"')
run(f'{NSSM} set BCR-forward-bot AppStdout "C:\\apps\\bot-keo-nhom-bcr-main\\logs\\forward_bot_out.log"')
run(f'{NSSM} set BCR-forward-bot AppStderr "C:\\apps\\bot-keo-nhom-bcr-main\\logs\\forward_bot_err.log"')
run(f'{NSSM} set BCR-forward-bot AppRestartDelay 5000')
run(f'{NSSM} start BCR-forward-bot')

# 2. Khởi động lại các session và bot BCR cũ
print("\n=== 2. RESTARTING BCR SERVICES ===")
for s in ['BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4', 'BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4']:
    run(f'{NSSM} restart {s}')

time.sleep(3)

# 3. Kiểm tra status và log
print("\n=== 3. CHECK STATUS & LOGS ===")
run(f'{NSSM} status BCR-forward-bot')
run(r'powershell -Command "if (Test-Path C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log) { Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log | Select-Object -Last 15 }"')
run(r'powershell -Command "if (Test-Path C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_err.log) { Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_err.log | Select-Object -Last 15 }"')

ssh.close()
