import paramiko
import sys

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

# Xem AppEnvironmentExtra của từng session
for s in ['BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4']:
    print(f"\n==================== {s} ====================")
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {s} AppEnvironmentExtra')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
