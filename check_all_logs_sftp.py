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

files = [
    'bot1-out.log', 'bot2-out.log', 'bot3-out.log', 'bot4-out.log',
    'bot1-err.log', 'bot2-err.log', 'bot3-err.log', 'bot4-err.log',
    'session1-out.log', 'session2-out.log', 'session3-out.log', 'session4-out.log',
    'server-out.log', 'server-err.log',
    'tele_out.log'
]

for filename in files:
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{filename}'
    print(f"\n==================== LOG: {filename} ====================")
    try:
        stat = sftp.stat(path)
        print(f"File size: {stat.st_size} bytes | Last modified: {stat.st_mtime}")
        with sftp.open(path, 'r') as f:
            f.seek(max(0, stat.st_size - 2500), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()[-15:]
            for l in lines:
                print(l)
    except Exception as e:
        print(f"Error: {e}")

sftp.close()
ssh.close()
