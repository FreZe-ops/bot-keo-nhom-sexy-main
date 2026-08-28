import paramiko
import sys

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

stdin, stdout, stderr = ssh.exec_command('schtasks /query /fo LIST | findstr /i "BCR Restart"')
print("Existing Tasks:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
