import paramiko
import os
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

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    return ssh

def run_cmd(ssh, cmd):
    print(f"\n>>> [VPS EXEC] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(out)
    if err.strip():
        print(f"[STDERR]: {err}")
    return out

def main():
    ssh = get_ssh()
    try:
        # 1. Kiểm tra PM2 và các tiến trình đang chạy
        print("=== 1. CHECK PM2 & PROCESSES ===")
        run_cmd(ssh, r'set PATH=C:\tools\node;C:\tools\git\cmd;C:\tools\python;C:\tools\python\Scripts;C:\tools\mongodb\bin;%PATH% & pm2 list')
        
        # 2. Đọc log lỗi server, session, bot
        print("\n=== 2. CHECK LOGS (LÝ DO DỪNG HÔ) ===")
        run_cmd(ssh, r'powershell -Command "Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\server-err.log | Select-Object -Last 25"')
        run_cmd(ssh, r'powershell -Command "Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\session1-err.log | Select-Object -Last 25"')
        run_cmd(ssh, r'powershell -Command "Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\session1-out.log | Select-Object -Last 25"')
        run_cmd(ssh, r'powershell -Command "Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\bot1-err.log | Select-Object -Last 25"')
        run_cmd(ssh, r'powershell -Command "Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\tele_out.log | Select-Object -Last 25"')

        # 3. Git pull repo mới
        print("\n=== 3. GIT PULL REPO TRÊN VPS ===")
        run_cmd(ssh, r'set PATH=C:\tools\git\cmd;%PATH% & cd /d C:\apps\bot-keo-nhom-bcr-main & git fetch origin main & git status & git pull origin main')

    finally:
        ssh.close()

if __name__ == '__main__':
    main()
