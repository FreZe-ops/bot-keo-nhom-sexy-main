import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

for b in ['BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4']:
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {b} Application')
    app = stdout.read().decode('utf-8', errors='replace').strip()
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {b} AppParameters')
    params = stdout.read().decode('utf-8', errors='replace').strip()
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {b} AppStdout')
    out_file = stdout.read().decode('utf-8', errors='replace').strip()
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get {b} AppStderr')
    err_file = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"{b}: App={app} Params={params} Out={out_file} Err={err_file}")

print("\nStarting BCR-bot2...")
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} start BCR-bot2')
print("Start BCR-bot2:", stdout.read().decode('utf-8', errors='replace').strip())

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} status BCR-bot2')
print("Status BCR-bot2:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
