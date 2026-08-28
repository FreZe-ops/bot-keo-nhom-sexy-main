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

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

for s in ['BCR-server', 'BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4', 'BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4']:
    print(f"\n==================== SERVICE: {s} ====================")
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {s} Application & {NSSM} get {s} AppParameters & {NSSM} get {s} AppEnvironmentExtra')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
