import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

cmd = r'cd /d C:\apps\bot-keo-nhom-bcr-main & git log -n 3 --oneline'
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Git log on VPS:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
