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
sftp = ssh.open_sftp()

for s in ['session1', 'session2', 'session3', 'session4']:
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{s}-out.log'
    print(f"\n==================== LOG: {s}-out.log ====================")
    try:
        with sftp.open(path, 'r') as f:
            f.seek(0, 2)
            sz = f.tell()
            f.seek(max(0, sz - 6000), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()
            for l in lines:
                if any(k in l.lower() for k in ['sodu', 'so du', 'số dư', 'balance', 'chip', 'autobet', 'place bet', 'cuoc', 'cược']):
                    print(l)
    except Exception as e:
        print(f"Error: {e}")

sftp.close()
ssh.close()
