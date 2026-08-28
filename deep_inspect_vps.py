import paramiko
import sys
import os

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
sftp = ssh.open_sftp()

print("==================== 1. DỊCH VỤ WINDOWS TRÊN VPS ====================")
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-server & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-session1 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-session2 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-session3 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-session4 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-bot1 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-bot2 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-bot3 & C:\tools\nssm\nssm-2.24\win64\nssm.exe status BCR-bot4')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n==================== 2. TIẾN TRÌNH PYTHON & NODE ====================")
stdin, stdout, stderr = ssh.exec_command('tasklist /FI "IMAGENAME eq node.exe" & tasklist /FI "IMAGENAME eq python.exe"')
print(stdout.read().decode('utf-8', errors='replace'))

def read_log_tail(filename, lines_count=15):
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{filename}'
    print(f"\n-------------------- {filename} --------------------")
    try:
        stat = sftp.stat(path)
        print(f"[File Size: {stat.st_size} bytes, Modified: {stat.st_mtime}]")
        with sftp.open(path, 'r') as f:
            f.seek(max(0, stat.st_size - 2500), 0)
            content = f.read().decode('utf-8', errors='replace').splitlines()[-lines_count:]
            for line in content:
                print(line)
    except Exception as e:
        print(f"Lỗi đọc {filename}: {e}")

for i in [1, 2, 3, 4]:
    read_log_tail(f'session{i}-out.log', 10)
    read_log_tail(f'session{i}-err.log', 10)

for i in [1, 2, 3, 4]:
    read_log_tail(f'bot{i}-out.log', 10)
    read_log_tail(f'bot{i}-err.log', 10)

sftp.close()
ssh.close()
