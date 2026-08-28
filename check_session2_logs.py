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

time.sleep(10)

def tail(name):
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{name}'
    print(f"\n==================== {name} ====================")
    try:
        with sftp.open(path, 'r') as f:
            f.seek(0, 2)
            sz = f.tell()
            f.seek(max(0, sz - 2000), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()[-10:]
            for l in lines:
                print(l)
    except Exception as e:
        print(f"Error: {e}")

tail('session2-out.log')
tail('session2-err.log')
tail('bot2-out.log')

sftp.close()
ssh.close()
