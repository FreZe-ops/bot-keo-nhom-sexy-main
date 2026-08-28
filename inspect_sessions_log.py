import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

for s in ['session1', 'session2', 'session3', 'session4']:
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{s}_out.log'
    print(f"\n==================== LOG: {s}_out.log (Last 10 lines) ====================")
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

sftp.close()
ssh.close()
