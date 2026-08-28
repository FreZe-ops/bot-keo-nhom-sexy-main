import paramiko
import time

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

for i in range(1, 7):
    time.sleep(6)
    path = 'C:/apps/bot-keo-nhom-bcr-main/logs/session2-out.log'
    try:
        with sftp.open(path, 'r') as f:
            f.seek(0, 2)
            sz = f.tell()
            f.seek(max(0, sz - 3000), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()[-12:]
            print(f"\n--- Check {i} ({time.strftime('%H:%M:%S')}) ---")
            for l in lines:
                print(l)
    except Exception as e:
        print(f"Error: {e}")

sftp.close()
ssh.close()
