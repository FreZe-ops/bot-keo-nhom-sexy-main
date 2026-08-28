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
    print(f"\n==================== [EXEC] {cmd} ====================")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print(f"[STDERR]: {err}")
    return out

run(r'C:\tools\nssm\nssm.exe status BCR-forward-bot')
run(r'C:\tools\nssm\nssm.exe status BCR-server')
run(r'C:\tools\nssm\nssm.exe status BCR-session1')
run(r'C:\tools\nssm\nssm.exe status BCR-bot1')

print("\n--- FORWARD BOT LOG ---")
run(r'powershell -Command "if (Test-Path C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log) { Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\forward_bot_out.log | Select-Object -Last 20 }"')

ssh.close()
