import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} start BCR-forward-bot')
print("Start BCR-forward-bot:")
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} status BCR-forward-bot')
print("Status BCR-forward-bot:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
